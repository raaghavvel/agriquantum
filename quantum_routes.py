"""Single-shipment, binary-index QAOA. No classical solution seeds or backfill."""
from copy import copy
from time import perf_counter
import numpy as np
import pandas as pd
from scipy.optimize import minimize, milp, Bounds, LinearConstraint
from problem_builder import ProblemBuilder


def candidates(loader, source_id, crop_id, quantity, deadline):
    if source_id not in set(loader.sources.source_id) or crop_id not in set(loader.crops.crop_id):
        raise ValueError('Select a source and crop from the dataset.')
    if not np.isfinite(quantity) or quantity <= 0 or not np.isfinite(deadline) or deadline <= 0:
        raise ValueError('Quantity and delivery hours must be positive finite numbers.')
    local = copy(loader)
    local.batches = pd.DataFrame([dict(batch_id='REQUEST', source_id=source_id,
        crop_id=crop_id, quantity_kg=quantity, max_delivery_hours=deadline)])
    p = ProblemBuilder(local).build(max_batches=1, all_markets=True)
    rows = []
    for m, market in enumerate(p.markets.itertuples()):
        # Single-shipment capacity is exact, not a pairwise approximation.
        if not p.feasible[0,m] or market.capacity_kg < quantity:
            continue
        price = loader.get_market_price(market.market_id, crop_id)
        # Do not recommend a destination using an invented fallback price.
        if price is None or not np.isfinite(price) or price <= 0:
            continue
        distance = loader.get_travel_distance(source_id, market.market_id)
        minutes = loader.get_travel_time(source_id, market.market_id)
        if not np.isfinite([distance, minutes]).all() or min(distance, minutes) < 0:
            continue
        rows.append(dict(market_id=market.market_id, market=market.market_name,
            latitude=float(market.latitude_num), longitude=float(market.longitude_num),
            price_per_kg=float(price), quantity_kg=quantity, distance_km=distance,
            travel_minutes=minutes, capacity_kg=float(market.capacity_kg),
            revenue=float(p.revenue[0,m]), transport_cost=float(p.transport_cost[0,m]),
            timing_penalty=float(p.late_penalty[0,m]),
            net_margin=float(p.revenue[0,m]-p.transport_cost[0,m]-p.late_penalty[0,m])))
    # Stable ID order; neither nearest distance nor classical profit sorting seeds QAOA.
    df = pd.DataFrame(rows)
    return (df.sort_values('market_id').reset_index(drop=True) if rows else df), float(p.unsold_penalty[0])


def evolve(energies, parameters):
    n = int(np.log2(len(energies)))
    depth = len(parameters)//2
    psi = np.ones(len(energies), dtype=complex)/np.sqrt(len(energies))
    for layer in range(depth):
        psi *= np.exp(-1j*parameters[layer]*energies)
        beta = parameters[depth+layer]
        for q in range(n):
            chunks = psi.reshape(-1, 2, 1 << q)
            a, b = chunks[:,0,:].copy(), chunks[:,1,:].copy()
            chunks[:,0,:] = np.cos(beta)*a - 1j*np.sin(beta)*b
            chunks[:,1,:] = np.cos(beta)*b - 1j*np.sin(beta)*a
    return psi


def solve_quantum(df, unsold_penalty, depth=2, iterations=80, shots=8192, seed=42):
    if df.empty:
        raise ValueError('No feasible markets with recorded prices and travel data.')
    if depth < 1 or iterations < 1 or shots < 1:
        raise ValueError('Depth, iterations and shots must be positive.')
    start = perf_counter()
    n = max(1, int(np.ceil(np.log2(len(df)+1))))
    # Last valid state means do not dispatch. Padded indices receive a high cost.
    values = np.append(df.net_margin.to_numpy(float), -unsold_penalty)
    scale = max(1., float(np.max(np.abs(values))))
    energies = np.full(2**n, 3.)
    energies[:len(values)] = -values/scale
    rng = np.random.default_rng(seed)
    best = None
    def objective(theta):
        return float(np.dot(np.abs(evolve(energies, theta))**2, energies))
    for _ in range(3):
        initial = rng.uniform(0.1, 1.0, 2*depth)
        fit = minimize(objective, initial, method='COBYLA', options={'maxiter':iterations})
        if best is None or fit.fun < best.fun:
            best = fit
    probabilities = np.abs(evolve(energies, best.x))**2
    probabilities /= probabilities.sum()
    counts = rng.multinomial(shots, probabilities)
    sampled = df.loc[counts[:len(df)] > 0].copy()
    sampled['shots'] = counts[:len(df)][counts[:len(df)] > 0]
    sampled['probability'] = probabilities[:len(df)][counts[:len(df)] > 0]
    sampled['bitstring'] = [format(i, f'0{n}b') for i in sampled.index]
    top = sampled.sort_values(['net_margin','market_id'], ascending=[False,True]).head(3).reset_index(drop=True)
    best_margin = float(top.iloc[0].net_margin) if not top.empty else None
    no_dispatch = counts[len(df)] > 0 and (best_margin is None or -unsold_penalty > best_margin)
    return dict(top=top, qubits=n, shots=shots, valid_market_shots=int(counts[:len(df)].sum()),
        invalid_shots=int(counts[len(values):].sum()), no_dispatch_shots=int(counts[len(df)]),
        no_dispatch=no_dispatch, objective=-unsold_penalty if no_dispatch else best_margin,
        seconds=perf_counter()-start, parameters=best.x.tolist(), expected_energy=float(best.fun))


def benchmarks(df, unsold_penalty, seed=42):
    """Called AFTER QAOA; never modifies its output."""
    values = np.append(df.net_margin.to_numpy(float), -unsold_penalty)
    rows = []
    start = perf_counter()
    result = milp(-values, integrality=np.ones(len(values)), bounds=Bounds(0,1),
        constraints=LinearConstraint(np.ones((1,len(values))),1,1))
    if not result.success:
        raise RuntimeError('MILP verification failed: '+result.message)
    exact = int(np.argmax(result.x))
    rows.append(dict(method='Exact MILP', objective=float(values[exact]), seconds=perf_counter()-start))
    start = perf_counter()
    greedy = int(np.argmax(values))
    rows.append(dict(method='Greedy (exact for one shipment)', objective=float(values[greedy]), seconds=perf_counter()-start))
    start = perf_counter()
    rng = np.random.default_rng(seed)
    state = int(rng.integers(len(values)))
    best = state
    for t in range(1000):
        other = int(rng.integers(len(values)))
        temperature = max(0.01, np.std(values)*(1-t/1000))
        if values[other] >= values[state] or rng.random() < np.exp((values[other]-values[state])/temperature):
            state = other
        if values[state] > values[best]:
            best = state
    rows.append(dict(method='Simulated annealing', objective=float(values[best]), seconds=perf_counter()-start))
    return pd.DataFrame(rows), exact

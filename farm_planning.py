"""Session-local farm inputs; never relabel collection-centre coordinates as farms."""
from copy import copy
import numpy as np
import pandas as pd


def farm_loader(base, farms, batches, road_factor=1.3, speed_kmh=35.0):
    farms, batches = farms.copy(), batches.copy()
    if farms.empty or batches.empty:
        raise ValueError('Add at least one farm and one crop batch.')
    for df, key in [(farms, 'source_id'), (batches, 'batch_id')]:
        if df[key].isna().any() or df[key].astype(str).str.strip().eq('').any() or df[key].duplicated().any():
            raise ValueError(f'{key} must be nonempty and unique.')
    for col, lo, hi in [('latitude', 8, 14), ('longitude', 76, 81)]:
        farms[col] = pd.to_numeric(farms[col], errors='coerce')
        if not farms[col].between(lo, hi).all():
            raise ValueError(f'Enter valid Tamil Nadu-region {col} values ({lo}–{hi}).')
    if not batches.source_id.isin(farms.source_id).all():
        raise ValueError('Every batch source_id must match an entered farm ID.')
    if not batches.crop_id.isin(base.crops.crop_id).all():
        raise ValueError('Select valid crop IDs from the crop reference.')
    for col in ['quantity_kg', 'max_delivery_hours']:
        batches[col] = pd.to_numeric(batches[col], errors='coerce')
        if not (np.isfinite(batches[col]) & (batches[col] > 0)).all():
            raise ValueError(f'{col} must contain positive finite numbers.')
    if road_factor < 1 or speed_kmh <= 0:
        raise ValueError('Road factor must be at least 1; speed must be positive.')
    farms['source_type'] = 'farm'
    farms['district'] = 'User-entered farm'
    for col in ['harvest_time', 'ready_time']:
        batches[col] = pd.Timestamp.now().floor('min')
    out = copy(base)
    out.sources, out.batches = farms, batches
    out.travel_dict = {}
    for farm in farms.itertuples():
        for market in base.markets.itertuples():
            lat1, lat2 = np.radians([farm.latitude, market.latitude_num])
            dl = np.radians(market.longitude_num - farm.longitude)
            a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dl/2)**2
            km = float(6371 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1))) * road_factor)
            out.travel_dict[(farm.source_id, market.market_id)] = (km, km / speed_kmh * 60)
    out.travel = pd.DataFrame([dict(origin_id=s, destination_id=m, distance_km=d, travel_minutes=t)
                              for (s,m),(d,t) in out.travel_dict.items()])
    return out


def route_data(problem, assignments, loader):
    routes, points = [], []
    for row in assignments.itertuples():
        batch = problem.batches.set_index('batch_id').loc[row.batch_id]
        src = loader.sources.set_index('source_id').loc[batch.source_id]
        dst = loader.markets.set_index('market_id').loc[row.market_id]
        distance = loader.get_travel_distance(batch.source_id, row.market_id)
        minutes = loader.get_travel_time(batch.source_id, row.market_id)
        crop = loader.crop_id_to_name.get(row.crop_id, row.crop_id)
        info = (f'{src.source_name} → {dst.market_name}\nBatch: {row.batch_id} | {crop}: {row.quantity_kg:g} kg'
                f'\nDistance: {distance:.1f} km | Travel: {minutes:.0f} min\nNet margin: Rs {row.net_profit:,.2f}')
        routes.append(dict(src_lon=float(src.longitude), src_lat=float(src.latitude),
                           dst_lon=float(dst.longitude_num), dst_lat=float(dst.latitude_num), tooltip=info,
                           batch_id=row.batch_id, source=src.source_name, market=dst.market_name, dst_name=dst.market_name,
                           distance_km=distance, travel_minutes=minutes, net_margin=row.net_profit))
        for name, lon, lat, kind in [(src.source_name, src.longitude, src.latitude, 'Source'),
                                    (dst.market_name, dst.longitude_num, dst.latitude_num, 'Market')]:
            points.append(dict(lon=float(lon), lat=float(lat), tooltip=f'{kind}: {name}\n{info}', kind=kind))
    return pd.DataFrame(routes), pd.DataFrame(points)

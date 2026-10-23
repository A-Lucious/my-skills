"""Structural baseline array analysis -> real Aseprite MCP job arguments.

Requires numpy, scipy and Pillow. Never draws or exports raster pixels itself.
"""
import json, hashlib, argparse
from pathlib import Path
from collections import Counter
from project_paths import ROOT as PROJECT, SKILL
import edge_topology as edge
import numpy as np
from PIL import Image
from scipy.ndimage import convolve, distance_transform_edt, binary_dilation, binary_erosion

def save(name,data):
    (ROOT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False))
def read(name): return json.loads((ROOT/name).read_text())
def raster(name): return np.array(Image.open(ROOT/name).convert('RGBA'))
def maps():
    g=read('guidance/surface-guidance.json')
    w,h=g['size']
    valid=np.zeros((h,w),bool); normal=np.zeros((h,w,3)); depth=np.zeros((h,w))
    obj=np.full((h,w),'',object); mat=obj.copy()
    for r in g['records']:
        x,y=r['xy']; valid[y,x]=True; normal[y,x]=r['normal_world']; depth[y,x]=r['ray_distance'];obj[y,x]=r['object'];mat[y,x]=r['material']
    return valid,normal,depth,obj,mat

def prepare():
    valid,normal,depth,obj,mat=maps()
    h,w=valid.shape
    config=read('guidance/prelight-manifest.json')
    if not valid.any():
        raise ValueError('The camera grid has no visible surface samples.')
    nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True)
    def gradient(a):
        if a.ndim==2: a=a[...,None]
        a=a[tuple(nearest)]
        gx=np.stack([convolve(a[...,i],edge.SOBEL_X,mode='nearest')/8 for i in range(a.shape[-1])],-1)
        gy=np.stack([convolve(a[...,i],edge.SOBEL_Y,mode='nearest')/8 for i in range(a.shape[-1])],-1)
        mag=np.sqrt((gx*gx+gy*gy).sum(-1))
        k=(gx*gx+gy*gy).argmax(-1);y,x=np.indices(k.shape)
        return mag,np.degrees(np.arctan2(gy[y,x,k],gx[y,x,k]))%180
    nm,na=gradient(normal);dm,da=gradient(depth)
    ax=convolve(valid.astype(float),edge.SOBEL_X,mode='constant')/8
    ay=convolve(valid.astype(float),edge.SOBEL_Y,mode='constant')/8
    am=np.hypot(ax,ay); aa=np.degrees(np.arctan2(ay,ax))%180
    alpha_edges=edge.nms(am,aa,.10)
    interior=binary_erosion(valid,structure=np.ones((3,3)))
    n_edges=edge.nms(nm,na,.12)&interior
    d_edges=edge.nms(dm,da,.08)&interior
    ids=np.zeros((h,w),bool)
    for dy,dx in [(0,1),(1,0)]:
        for y in range(h-dy):
            for x in range(w-dx):
                yy,xx=y+dy,x+dx
                if valid[y,x] and valid[yy,xx] and (mat[y,x]!=mat[yy,xx] or obj[y,x]!=obj[yy,xx]):
                    ids[y,x]=ids[yy,xx]=True
    raw=alpha_edges|n_edges|d_edges|ids
    thin=edge.thinning(raw);clean,_=edge.perfect_pixel(thin)
    candidates=thin&~clean&valid
    counts=Counter(obj[valid]);small=np.array([[bool(valid[y,x] and (counts[obj[y,x]]<=40 or ('gold' in config['material_families'][mat[y,x]] or mat[y,x] in config['protected_materials']))) for x in range(w)] for y in range(h)])
    degree=convolve(thin.astype(int),np.ones((3,3),int),mode='constant')-thin
    special=thin&((degree<=1)|(degree>=3))
    protected=small|special
    # 1px Chebyshev band around the cleaned structure, with removed corners retained
    # as candidates. Keep alpha/part/material edge coverage even at junctions.
    band=binary_dilation(clean,structure=np.ones((3,3)))&valid
    save('guidance/structure.json',{'version':'2.0.0','surface_sha256':hashlib.sha256((ROOT/'guidance/surface-guidance.json').read_bytes()).hexdigest(),'parameters':{'normal_sobel_threshold':.12,'depth_sobel_threshold_world':.08,'alpha_threshold':.10,'kernel_divisor':8,'protection_radius_px':1,'small_part_max_pixels':40,'alpha_edit':False},'edge_xy':np.argwhere(clean)[:,::-1].tolist(),'candidate_xy':np.argwhere(candidates)[:,::-1].tolist(),'protected_xy':np.argwhere(protected)[:,::-1].tolist(),'band_xy':np.argwhere(band)[:,::-1].tolist(),'metrics':{'ray_hits':int(valid.sum()),'alpha_edges':int(alpha_edges.sum()),'normal_edges':int(n_edges.sum()),'depth_edges':int(d_edges.sum()),'identity_boundary_pixels':int(ids.sum()),'thin_pixels':int(thin.sum()),'clean_pixels':int(clean.sum()),'corner_candidates':int(candidates.sum()),'protected_candidates':int((candidates&protected).sum()),'band_pixels':int(band.sum()),'band_percent':round(100*band.sum()/valid.sum(),2)}})
    pixels=[{'x':x,'y':y,'color':'#000000ff' if band[y,x] else '#ffffffff'} for y in range(h) for x in range(w)]
    save('reports/mask-pixels.json',{'filename':f'{REL}/source/dither-mask.aseprite','frame':1,'layer':'mask','pixels':pixels})
    args=read('reports/mask-pixels.json')
    job={'steps':[
        {'tool':'create_sprite','arguments':{'filename':args['filename'],'width':w,'height':h,'color_mode':'rgb'}},
        {'tool':'rename_layer','arguments':{'filename':args['filename'],'layer':'Layer 1','new_name':'mask'}},
        {'tool':'draw_pixels','arguments':args},
        {'tool':'export_png','arguments':{'filename':args['filename'],'output':f'{REL}/guidance/dither-mask.png'}}]}
    save('reports/mask.job.json',job)
    print(json.dumps(read('guidance/structure.json')['metrics']))


def cleanup():
    valid, normal, depth, obj, mat = maps()
    h, w = valid.shape
    structure = read('guidance/structure.json')
    manifest = read('shader/shader-manifest.json')
    config = read('guidance/prelight-manifest.json')
    if manifest['version'] != '2.0.0':
        raise ValueError('Use the current structural baseline Shader output.')
    if manifest['surface_sha256'] != structure['surface_sha256']:
        raise ValueError('Shader and structural candidates have different guidance.')
    protected = {tuple(p) for p in structure['protected_xy']}
    palette_path = SKILL/'styles/parchment-fantasy/palette.json'
    palette = json.loads(palette_path.read_text())['families']
    mapping = config['material_families']
    light = raster('shader/lighting-native.png')[...,:3].astype(float)/255
    img = raster('shader/pixel-base-v01.png')
    if img.shape[:2] != valid.shape:
        raise ValueError('Shader and guidance grids differ.')
    changes, skipped = [], Counter()
    for x, y in structure['candidate_xy']:
        old = tuple(img[y,x])
        if old[3] == 0 or not valid[y,x]:
            skipped['background_or_no_ray'] += 1; continue
        if (x,y) in protected:
            skipped['protected_landmark_or_junction'] += 1; continue
        allowed = [c for f in mapping[mat[y,x]] for c in palette[f]['ramp']]
        oldhex = '#'+''.join(f'{int(v):02x}' for v in old[:3])
        neighbours = []
        for yy in range(max(0,y-1),min(h,y+2)):
            for xx in range(max(0,x-1),min(w,x+2)):
                if (xx,yy)==(x,y) or not img[yy,xx,3]: continue
                color = tuple(img[yy,xx])
                if color == old or obj[yy,xx]!=obj[y,x] or mat[yy,xx]!=mat[y,x]: continue
                if np.dot(normal[yy,xx],normal[y,x]) < .90 or abs(depth[yy,xx]-depth[y,x]) > .15: continue
                if np.linalg.norm(light[yy,xx]-light[y,x]) > .12: continue
                hx = '#'+''.join(f'{int(v):02x}' for v in color[:3])
                if hx not in allowed or oldhex not in allowed or abs(allowed.index(hx)-allowed.index(oldhex)) > 2: continue
                neighbours.append((color,xx,yy))
        counts = Counter(n[0] for n in neighbours)
        if not counts:
            skipped['no_safe_source_color'] += 1; continue
        target = sorted(counts,key=lambda c:(-counts[c],c))[0]
        if counts[target] < 2:
            skipped['insufficient_support'] += 1; continue
        source_xy = next([xx,yy] for c,xx,yy in neighbours if c==target)
        changes.append({'x':x,'y':y,'color':'#'+''.join(f'{int(v):02x}' for v in target[:3])+f'{int(old[3]):02x}',
                        'from':'#'+''.join(f'{int(v):02x}' for v in old),
                        'source_xy':source_xy,'object':obj[y,x],'material':mat[y,x]})
    filename = f'{REL}/source/draft.aseprite'
    pixels = [{k:p[k] for k in ['x','y','color']} for p in changes]
    report = {'version':'2.0.0','candidate_pixels':len(structure['candidate_xy']),
              'recoloured_pixels':len(changes),'skipped':dict(skipped),'changes':changes}
    save('reports/cleanup.json',report)
    steps = [
        {'tool':'import_image','arguments':{'input_image':f'{REL}/shader/pixel-base-v01.png','output':filename}},
        {'tool':'rename_layer','arguments':{'filename':filename,'layer':'Layer','new_name':'base-ref'}},
        {'tool':'add_layer','arguments':{'filename':filename,'name':'draft'}},
        {'tool':'stamp_file','arguments':{'filename':filename,'source':f'{REL}/shader/pixel-base-v01.png','x':0,'y':0,'layer':'draft','frame':1}},
        {'tool':'set_layer_properties','arguments':{'filename':filename,'layer':'base-ref','visible':False,'editable':False}}]
    if pixels:
        steps.append({'tool':'draw_pixels','arguments':{'filename':filename,'pixels':pixels,'layer':'draft','frame':1}})
    steps += [{'tool':'export_png','arguments':{'filename':filename,'output':f'{REL}/exports/pixel.png'}},
              {'tool':'get_sprite_info','arguments':{'filename':filename}}]
    save('reports/cleanup.job.json',{'steps':steps})
    print(json.dumps({k:v for k,v in report.items() if k!='changes'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['prepare','cleanup'])
    parser.add_argument('--task',required=True,help='Task directory relative to Test Workspace')
    args = parser.parse_args()
    workspace = (PROJECT/'Test Workspace').resolve()
    ROOT = (workspace/args.task).resolve()
    if ROOT == workspace or not ROOT.is_relative_to(workspace):
        parser.error('Use a task subdirectory inside Test Workspace.')
    REL = ROOT.relative_to(workspace).as_posix()
    (ROOT/'reports').mkdir(parents=True,exist_ok=True)
    (ROOT/'source').mkdir(parents=True,exist_ok=True)
    {'prepare':prepare,'cleanup':cleanup}[args.stage]()

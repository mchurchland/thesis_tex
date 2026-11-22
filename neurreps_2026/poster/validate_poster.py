#!/usr/bin/env python3
"""Check poster layout, plotted data, fonts and an independent Overleaf build."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
import pandas as pd
from PIL import Image

HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def command(args,cwd=HERE):
    r=subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode:raise RuntimeError(f'{args[0]} failed: {r.stdout[-2000:]} {r.stderr[-2000:]}')
    return r.stdout


def main():
    source=json.loads((HERE/'poster_sources.json').read_text())
    assert sha(HERE/'build_figures.py')==source['figure_script_sha256']
    for name,digest in source['outputs'].items():assert sha(HERE/'assets'/name)==digest,name
    for name,digest in source['data_outputs'].items():assert sha(HERE/name)==digest,name
    assert all(not s['figure_text_clipped'] for s in source['selections'].values())
    network=json.loads((HERE/'poster_data/edge_sign_schematic.json').read_text())
    assert len(network)==3
    previous=set();edge_counts=[]
    for r in network:
        assert r['realization']==1 and r['seed']==network[0]['seed']
        assert r['edges']==network[0]['edges'] and r['positions']==network[0]['positions']
        assert r['edge_order']==network[0]['edge_order']
        assert len({i for edge in r['edges'] for i in edge})==5 and len(r['edges'])==10
        selected=set(r['negative_indices']);assert previous<=selected;previous=selected
        assert len(selected)==int(10*r['fraction']);edge_counts.append(len(selected))
    assert edge_counts==[0,2,5]
    audit=json.loads((HERE/'poster_data/sign_nesting_audit.json').read_text())
    assert audit['realizations']==100 and audit['checks']==300 and audit['all_nested']
    assert all(r['lost_from_20_to_50']==0 for r in audit['records'])
    curves=pd.read_csv(HERE/'poster_data/mc_input_curves.csv')
    inset=pd.read_csv(HERE/'poster_data/mc_auc_inset.csv')
    assert len(curves)==44 and sorted(curves.input_scale.unique())==[.01,.5]
    assert len(inset)==4 and sorted(inset.input_scale.unique())==[.01,.5]
    for (family,inp),g in curves.groupby(['family','input_scale']):
        g=g.sort_values('negative_fraction')
        expected=np.trapezoid(g['mean'],g.negative_fraction)/np.ptp(g.negative_fraction)
        observed=inset[(inset.family==family)&(inset.input_scale==inp)].performance_auc
        assert len(observed)==1;np.testing.assert_allclose(observed.iloc[0],expected,rtol=1e-12)
    narma=pd.read_csv(HERE/'poster_data/narma_mean_curves.csv')
    assert len(narma)==22 and set(narma.input_scale)=={'ALL'}
    narma_auc=pd.read_csv(HERE/'poster_data/narma_auc.csv')
    for family,g in narma.groupby('family'):
        g=g.sort_values('negative_fraction')
        expected=np.trapezoid(g['mean'],g.negative_fraction)/np.ptp(g.negative_fraction)
        observed=narma_auc[(narma_auc.suite=='architecture')&(narma_auc.family==family)].performance_auc
        assert len(observed)==1;np.testing.assert_allclose(observed.iloc[0],expected,rtol=1e-12)
    topology=pd.read_csv(HERE/'poster_data/structural_mc_auc.csv')
    assert set(topology[topology.group=='Topology, all binary weights'].family)=={'ce_binary','er_binary','ws_binary'}
    log=(HERE/'poster.log').read_text()
    assert not any(token in log for token in ['POSTER LAYOUT:','Overfull \\hbox','Overfull \\vbox','Missing character:'])
    blocks=re.findall(r'POSTER BLOCK ([^:]+): height=([.0-9]+)pt, budget=([.0-9]+)cm',log)
    assert len(blocks)>=40
    for name,height,budget in blocks:assert float(height)/28.4527559<=float(budget)+.005,name
    info=command(['pdfinfo','poster.pdf']);assert re.search(r'Pages:\s+1\b',info)
    width,height=map(float,re.search(r'Page size:\s+([.0-9]+) x ([.0-9]+)',info).groups())
    np.testing.assert_allclose(np.array([width,height])*2.54/72,[61,85],atol=.005)
    fonts=command(['pdffonts','poster.pdf'])
    font_flags=re.findall(r'\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$',fonts,re.M)
    assert font_flags and all(flags[0]=='yes' for flags in font_flags)
    text=command(['pdftotext','poster.pdf','-'])
    peaks=pd.read_csv(HERE/'poster_data/peak_mc200_ordering.csv')
    assert len(peaks)==12 and peaks.maximum_seed_mean_MC200.is_monotonic_decreasing
    displayed_peaks=pd.concat([peaks.head(3),peaks[peaks.family=='ce_empirical']])
    assert list(displayed_peaks.family)==['ws_binary','er_binary','ws_halfnormal','ce_empirical']
    for value in displayed_peaks.maximum_seed_mean_MC200:assert f'{value:.2f}' in text
    assert '1.94%' in re.sub(r'\s+','',text) and '0.89%' in re.sub(r'\s+','',text)
    with tempfile.TemporaryDirectory(prefix='neurreps-poster-check-') as tmp:
        tmp=Path(tmp);bounds=tmp/'bbox.html'
        command(['pdftotext','-bbox-layout',str(HERE/'poster.pdf'),str(bounds)])
        ns={'x':'http://www.w3.org/1999/xhtml'};pages=ET.parse(bounds).findall('.//x:page',ns)
        assert len(pages)==1;words=pages[0].findall('.//x:word',ns)
        for word in words:
            a=word.attrib
            assert float(a['xMin'])>=-.5 and float(a['yMin'])>=-.5
            assert float(a['xMax'])<=width+.5 and float(a['yMax'])<=height+.5
        command(['pdfimages','-png',str(HERE/'poster.pdf'),str(tmp/'embedded')])
        embedded=[]
        for f in tmp.glob('embedded-*.png'):
            with Image.open(f) as im:
                if im.mode in ('RGB','RGBA'):embedded.append(np.asarray(im.convert('RGB')))
        for name in source['outputs']:
            with Image.open(HERE/'assets'/name) as im:expected=np.asarray(im.convert('RGB'))
            assert any(a.shape==expected.shape and np.array_equal(a,expected) for a in embedded),f'PDF contains stale figure: {name}'
        members=['poster.tex','README.txt','SOURCES.md','poster_sources.json','build_figures.py','validate_poster.py']
        members += ['assets/'+name for name in source['outputs']]
        members += list(source['data_outputs'])
        archive=HERE/'neurreps_overleaf.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name in members:z.write(HERE/name,name)
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None;z.extractall(tmp/'project')
        build=command(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','poster.tex'],tmp/'project')
        packed_text=command(['pdftotext','poster.pdf','-'],tmp/'project')
        assert packed_text==text,'Independent package differs'
    result=dict(revision='MC200 sketch; linear MC plot for inputs 0.01/0.5; NARMA curves averaged across all 24 settings',
        pages=1,size_cm=[61,85],layout_blocks=len(blocks),layout_budget_warnings=0,overfull_boxes=0,missing_glyphs=0,
        text_bounds_checked=len(words),text_outside_page=0,all_fonts_embedded=True,
        figure_hashes_verified=len(source['outputs']),figure_text_clipping=False,embedded_figure_pixels_match_sources=True,
        schematic_realizations=1,schematic_nodes=5,schematic_edges=10,schematic_negative_counts=edge_counts,
        schematic_layout='Kamada–Kawai, fixed across fractions; not a ring',
        input_strengths=[.01,.1,.5,1.5],mc_display_inputs=[.01,.5],mc_axis_scale='linear',mc_inset_auc_matches_curves=True,narma_curve_points=22,narma_aggregation='all 24 settings',narma_auc_matches_curves=True,
        topology_comparison='binary CE, ER and WS-like weights under own-radius scaling',peak_ordering='top three plus original CE (rank 11); full 12-model ordering retained in CSV',
        independent_package_compile='passed',independent_package_text_matches=True,archive_members=members,
        previous_poster='archive/before_sketch_mc200_2026-11-22/',
        artifacts={name:sha(HERE/name) for name in ['poster.tex','poster.pdf','poster_preview.png','neurreps_overleaf.zip']})
    (HERE/'poster_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['archive_members','artifacts']},indent=2),flush=True)


if __name__=='__main__':main()

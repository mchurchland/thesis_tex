#!/usr/bin/env python3
"""MC200 poster figures following the user's November 22 panel sketch.

All plotted performance is from stored, checksum-verified summaries. The edge
diagram illustrates the actual nested sign-quota rule; it is not a CE subgraph.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
os.environ.setdefault('MPLCONFIGDIR','/tmp/matplotlib-neurreps-poster-mc200')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/neurreps-poster-mc200-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT))
from network_stats.architecture_sweep import rng_for
from util.ei_auc import curve_areas

ANALYSIS=ROOT/'analysis/mc200_recompute/mc200_274500'
OUT=HERE/'assets';DATA=HERE/'poster_data'
INK='#192F40';MUTED='#526674';TEAL='#007D80';CE='#D55E00';ER='#0072B2';GAMMA='#A42B77'
COLORS={'ce_empirical':CE,'ce_shuffled':'#E69F00','ce_degree_rewired':'#CC79A7',
        'er_signed_empirical':'#7A3E8E','ws_signed_empirical':'#332288',
        'er_binary':ER,'er_halfnormal':'#A77300','ws_binary':'#666666',
        'ws_halfnormal':'#55A6C8','ce_binary':'#882255','ce_halfnormal':'#AA4499',
        'ce_unknown_removed':'#526674'}
INPUTS={};SELECTIONS={}


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
    return h.hexdigest()


def table(relative):
    path=ANALYSIS/relative;m=json.loads((ANALYSIS/'manifest.json').read_text())
    assert digest(path)==m['outputs'][relative],f'Changed analysis table: {relative}'
    INPUTS[str(path.relative_to(ROOT))]=digest(path)
    return pd.read_csv(path)


def save(fig,name,selection):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer();bounds=fig.bbox
    texts=list(fig.texts)
    for ax in fig.axes:texts.extend([ax.title,ax._left_title,ax._right_title,ax.xaxis.label,ax.yaxis.label])
    for legend in fig.legends:texts.extend(legend.get_texts());texts.append(legend.get_title())
    checked=0
    for text in texts:
        if not text.get_visible() or not text.get_text().strip():continue
        box=text.get_window_extent(renderer)
        if box.x0 < -2 or box.y0 < -2 or box.x1 > bounds.width+2 or box.y1 > bounds.height+2:
            raise ValueError(f'Clipped figure text in {name}: {text.get_text()}')
        checked+=1
    selection=dict(selection,figure_text_bounds_checked=checked,figure_text_clipped=False)
    fig.savefig(OUT/name,dpi=400,facecolor='white')
    plt.close(fig);SELECTIONS[name]=selection


def clean(ax):
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['bottom','left']].set_color('#8B9BA5')
    ax.tick_params(colors=MUTED,length=3)
    ax.grid(axis='y',color='#DDE5E8',lw=.7)
    ax.set_axisbelow(True)


def sign_sweep():
    # Deliberately small, explicitly labeled schematic: exact quotas are visible.
    graph=nx.DiGraph([(0,1),(1,0),(0,2),(2,0),(0,3),(3,0),(0,4),(4,0),(1,2),(3,4)])
    assert nx.is_weakly_connected(graph)
    edges=list(graph.edges());positions=nx.kamada_kawai_layout(graph.to_undirected(),weight=None)
    coordinates=np.asarray(list(positions.values()))
    middle=(coordinates.min(axis=0)+coordinates.max(axis=0))/2
    half_width=np.ptp(coordinates,axis=0).max()*.64
    fractions=[0.,.2,.5];seed=20261119;records=[]
    order=rng_for(seed,'CE nested sign order').permutation(len(edges))
    fig,axes=plt.subplots(1,3,figsize=(10.6,4.1))
    fig.subplots_adjust(left=.025,right=.975,bottom=.21,top=.80,wspace=.12)
    previous=set()
    for ax,fraction in zip(axes,fractions):
        selected=set(order[:int(fraction*len(edges))]);assert previous<=selected;previous=selected
        positive=[e for j,e in enumerate(edges) if j not in selected]
        negative=[e for j,e in enumerate(edges) if j in selected]
        nx.draw_networkx_edges(graph,positions,edgelist=positive,ax=ax,edge_color='#3384AC',width=1.7,
            arrows=True,arrowsize=16,node_size=390,connectionstyle='arc3,rad=0.16')
        nx.draw_networkx_edges(graph,positions,edgelist=negative,ax=ax,edge_color='#C23B4A',width=2.2,
            arrows=True,arrowsize=16,node_size=390,connectionstyle='arc3,rad=0.16')
        nx.draw_networkx_nodes(graph,positions,ax=ax,node_size=390,node_color='#EFF3F5',edgecolors=INK,linewidths=1)
        nx.draw_networkx_labels(graph,positions,labels={i:str(i+1) for i in graph},ax=ax,font_size=12,font_color=INK)
        ax.set_xlim(middle[0]-half_width,middle[0]+half_width)
        ax.set_ylim(middle[1]-half_width,middle[1]+half_width)
        ax.set_aspect('equal',adjustable='box');ax.axis('off')
        ax.set_title(f'{fraction:.0%} inhibitory edges',fontsize=17,color=INK,pad=9)
        ax.text(.5,-.10,f'{len(negative)} of {len(edges)} edges negative',ha='center',transform=ax.transAxes,fontsize=14,color=MUTED)
        records.append(dict(realization=1,seed=seed,fraction=fraction,negative_indices=list(map(int,sorted(selected))),
                            edge_order=order.tolist(),edges=[list(e) for e in edges],positions={str(i):p.tolist() for i,p in positions.items()}))
    fig.text(.5,.97,'One realization: the same connections and random edge order',
             fontsize=17,weight='bold',color=INK,va='top',ha='center')
    fig.legend([Line2D([0],[0],color='#3384AC',lw=2),Line2D([0],[0],color='#C23B4A',lw=2.5)],
               ['Excitatory edge (+)','Inhibitory edge (−)'],loc='lower center',ncol=2,frameon=False,fontsize=15)
    (DATA/'edge_sign_schematic.json').write_text(json.dumps(records,indent=2)+'\n')
    save(fig,'poster_edge_sign_sweep.png',dict(kind='five-node, ten-edge illustrative schematic, not a CE subgraph',
        fractions=fractions,seeds=[seed],
        layout='Kamada–Kawai layout of the undirected projection of one fixed directed schematic; not a ring',
        rule='One random order per realization; flip prefix floor(p*M); nested within realization; redraw across realizations',
        sign_rule_source='network_stats/architecture_sweep.py: raw_networks',nodes='neutral; signs assigned to edges, not neuron types'))


def inset_auc(ax,metric):
    auc=table('architecture/performance_auc.csv')
    auc=auc[(auc.normalization=='own_radius')&(auc.metric==metric)&(auc.input_scale=='ALL')].set_index('family')
    for y,family,color in [(1,'ce_empirical',CE),(0,'er_binary',ER)]:
        r=auc.loc[family]
        ax.hlines(y,r.ci_low,r.ci_high,color=color,lw=1.8)
        ax.scatter(r.performance_auc,y,color=color,s=30,zorder=3)
    ax.set(yticks=[1,0],yticklabels=['CE','ER'],ylim=(-.6,1.7))
    ax.set_title('Mean-performance AUC',fontsize=11.8,color=INK,pad=2)
    ax.tick_params(axis='both',labelsize=11.5,length=2,pad=2)
    ax.spines[['top','right','left']].set_visible(False)
    ax.tick_params(axis='y',length=0)
    if metric=='MC_200':ax.set_xlim(10.3,15.8);ax.set_xticks([11,13,15])
    else:ax.set_xlim(.17,.205);ax.set_xticks([.18,.20])
    return auc.loc[['ce_empirical','er_binary']].reset_index()


def mc_curves():
    d=table('architecture/mean_performance.csv')
    inputs=[.01,.5];colors=['#332288','#009E73']
    chosen=d[(d.normalization=='own_radius')&(d.metric=='MC_200')&d.family.isin(['ce_empirical','er_binary'])&d.input_scale.isin([str(v) for v in inputs])].copy()
    chosen.to_csv(DATA/'mc_input_curves.csv',index=False)
    fig=plt.figure(figsize=(7.2,6.5));ax=fig.add_axes([.13,.12,.83,.61])
    for inp,color in zip(inputs,colors):
        curves={}
        for family,ls in [('ce_empirical','-'),('er_binary','--')]:
            g=chosen[(chosen.family==family)&(chosen.input_scale==str(inp))].sort_values('negative_fraction')
            assert len(g)==11;curves[family]=g['mean'].to_numpy();x=g.negative_fraction.to_numpy()*100
            ax.plot(x,g['mean'],color=color,lw=2.1,ls=ls,marker='o' if family=='ce_empirical' else None,ms=3)
            ax.fill_between(x,g.ci_low,g.ci_high,color=color,alpha=.055,lw=0)
        ax.fill_between(x,curves['ce_empirical'],curves['er_binary'],where=curves['ce_empirical']>=curves['er_binary'],
                        interpolate=True,color=color,alpha=.24,lw=0)
    assert chosen['mean'].min()>7.5 and chosen['mean'].max()<39.5
    ax.set(xlabel='Inhibitory edges (%)',ylabel='MC200',xticks=[0,20,40,60,80,100],xlim=(-2,102),ylim=(7.5,39.5),yticks=[8,10,20,30,38]);clean(ax)
    fig.legend([Line2D([0],[0],color=color,lw=2.5) for color in colors],[f'Input {inp:g}' for inp in inputs],
               loc='upper left',bbox_to_anchor=(.045,.995),frameon=False,fontsize=13,ncol=2,columnspacing=1,handlelength=1.5)
    fig.legend([Line2D([0],[0],color=INK,lw=2),Line2D([0],[0],color=INK,lw=2,ls='--')],['CE','ER binary'],
               loc='upper left',bbox_to_anchor=(.045,.855),frameon=False,fontsize=13,ncol=2,handlelength=1.5)
    auc=table('architecture/performance_auc.csv')
    auc=auc[(auc.normalization=='own_radius')&(auc.metric=='MC_200')&auc.input_scale.isin([str(v) for v in inputs])&auc.family.isin(['ce_empirical','er_binary'])]
    iax=fig.add_axes([.66,.815,.29,.15])
    for y,(inp,color) in enumerate(zip(inputs,colors)):
        for family,offset,marker in [('ce_empirical',.10,'o'),('er_binary',-.10,'s')]:
            r=auc[(auc.family==family)&(auc.input_scale==str(inp))].iloc[0]
            iax.hlines(y+offset,r.ci_low,r.ci_high,color=color,lw=1.1);iax.scatter(r.performance_auc,y+offset,color=color,marker=marker,s=16)
    iax.set(yticks=range(len(inputs)),yticklabels=[f'{v:g}' for v in inputs],ylim=(len(inputs)-.5,-.5),xlim=(8,24),xticks=[8,16,24])
    iax.set_title('AUC: ○ CE, □ ER',fontsize=10.5,color=INK,pad=3);iax.tick_params(labelsize=10.5,length=2,pad=2)
    iax.spines[['top','right']].set_visible(False)
    auc.to_csv(DATA/'mc_auc_inset.csv',index=False)
    save(fig,'poster_mc_input_curves.png',dict(metric='MC_200',normalization='own_radius',
        families=['ce_empirical','er_binary'],inputs=inputs,aggregation='six radius/leak settings per input; 100 paired realizations',
        inset='normal performance AUC for each input over its six radius/leak settings; circles CE, squares ER; not win AUC',
        zoom='linear y axis, limits 7.5–39.5 retain every plotted mean; colored fill marks CE advantage'))


def structure_auc():
    d=table('architecture/performance_auc.csv')
    d=d[(d.normalization=='own_radius')&(d.metric=='MC_200')&(d.input_scale=='ALL')].set_index('family')
    groups=[('Empirical weight placement', [('ce_empirical','CE original'),('ce_shuffled','CE shuffled weights')]),
            ('Topology, all binary weights',[('ce_binary','CE topology'),('er_binary','ER topology'),('ws_binary','WS-like topology')]),
            ('Magnitude distribution on ER',[('er_binary','Binary'),('er_halfnormal','Half-normal'),('er_signed_empirical','CE magnitudes')])]
    fig,axes=plt.subplots(3,1,figsize=(7.15,6.0),sharex=True)
    fig.subplots_adjust(left=.44,right=.96,bottom=.13,top=.91,hspace=.85)
    displayed=[]
    for ax,(title,models) in zip(axes,groups):
        for y,(family,label) in enumerate(models):
            r=d.loc[family];color=COLORS[family]
            ax.hlines(y,r.ci_low,r.ci_high,color=color,lw=2)
            ax.scatter(r.performance_auc,y,color=color,s=48,marker='D' if family=='ce_empirical' else 'o',zorder=3)
            displayed.append(dict(group=title,label=label,**r.to_dict(),family=family))
        ax.set(yticks=range(len(models)),yticklabels=[label for _,label in models],ylim=(len(models)-.5,-.5),xlim=(10.4,18.7))
        ax.set_title(title,loc='left',fontsize=15.5,weight='bold',color=INK,pad=9)
        ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0,pad=7,labelsize=14.5)
        ax.grid(axis='x',color='#DDE5E8',lw=.7);ax.set_axisbelow(True)
    axes[-1].set_xticks([11,14,17]);axes[-1].set_xlabel('Mean MC200 AUC  (higher is better)',fontsize=14.5)
    pd.DataFrame(displayed).to_csv(DATA/'structural_mc_auc.csv',index=False)
    save(fig,'poster_structural_mc_auc.png',dict(metric='MC_200',normalization='own_radius',groups=groups,
        aggregation='all 24 settings, E/I AUC divided by observed span; 95% paired-realization intervals',
        caveat='Own-radius scaling changes effective magnitude units between matrices; shared-scaling check shown in critics corner'))


def weight_auc():
    d=table('er/performance_auc.csv')
    d=d[(d.normalization=='own_radius')&(d.metric=='MC_200')&(d.input_scale=='ALL')].set_index('family')
    families=['empirical','binary','halfnormal','cap99','cap95','cap90','gamma','lognormal','hetero50','hetero75']
    names=['Empirical CE','Binary','Half-normal','Cap Q99','Cap Q95','Cap Q90','Matched gamma','Matched lognormal','Compress a=0.50','Compress a=0.75']
    colors=[CE,'#777777','#777777','#0072B2','#0072B2','#0072B2',GAMMA,'#44AA99','#7A3E8E','#7A3E8E']
    fig,ax=plt.subplots(figsize=(7.15,5.55));fig.subplots_adjust(left=.43,right=.96,bottom=.14,top=.97)
    ax.axvline(d.loc['empirical','performance_auc'],ls=':',color=CE,lw=1.2,zorder=0)
    ax.axhspan(5.6,6.4,color='#F4E7F0',zorder=0)
    for y,family,color in zip(range(len(families)),families,colors):
        r=d.loc[family];ax.hlines(y,r.ci_low,r.ci_high,color=color,lw=2)
        ax.scatter(r.performance_auc,y,color=color,s=52 if family=='gamma' else 38,zorder=3,marker='D' if family=='gamma' else 'o')
    ax.set(yticks=range(len(families)),yticklabels=names,ylim=(9.6,-.6),xlim=(14.6,17.05),xticks=[15,16,17],xlabel='Mean MC200 AUC')
    ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0,pad=7,labelsize=14.5)
    ax.grid(axis='x',color='#DDE5E8',lw=.7);ax.set_axisbelow(True)
    d.loc[families].reset_index().to_csv(DATA/'er_weight_mc_auc.csv',index=False)
    save(fig,'poster_er_weight_mc_auc.png',dict(metric='MC_200',normalization='own_radius',families=families,
        aggregation='all 24 settings, normal performance AUC; 95% paired-realization intervals',
        modifications='caps restore mean magnitude; gamma/lognormal match finite mean/variance and preserve ER ranks; compression w=mu+a*(w-mu)'))


def narma():
    a=table('architecture/performance_auc.csv');e=table('er/performance_auc.csv');curves=table('architecture/mean_performance.csv')
    mean_curves=curves[(curves.normalization=='own_radius')&(curves.metric=='NARMA10_test_nmse')&curves.family.isin(['ce_empirical','er_binary'])&(curves.input_scale=='ALL')].copy()
    mean_curves.to_csv(DATA/'narma_mean_curves.csv',index=False)
    selected=[('architecture','ce_empirical','CE original'),('architecture','ce_shuffled','CE shuffled'),
              ('architecture','er_binary','ER binary'),('architecture','er_signed_empirical','ER + CE weights'),
              ('architecture','ws_signed_empirical','WS-like + CE weights'),('er','gamma','ER + gamma'),('er','lognormal','ER + lognormal')]
    fig=plt.figure(figsize=(7.15,7.0));ax=fig.add_axes([.43,.59,.53,.36]);rows=[]
    for y,(suite,family,label) in enumerate(selected):
        d=a if suite=='architecture' else e
        g=d[(d.family==family)&(d.normalization=='own_radius')&(d.metric=='NARMA10_test_nmse')&(d.input_scale=='ALL')]
        assert len(g)==1;r=g.iloc[0];color=COLORS.get(family,GAMMA if family=='gamma' else '#44AA99')
        ax.hlines(y,r.ci_low,r.ci_high,color=color,lw=2);ax.scatter(r.performance_auc,y,color=color,s=40)
        rows.append(dict(suite=suite,label=label,**r.to_dict()))
    ax.set(yticks=range(len(selected)),yticklabels=[label for _,_,label in selected],ylim=(6.6,-.6),xlim=(.142,.204),xticks=[.15,.17,.19],xlabel='NMSE AUC  (lower is better)')
    ax.tick_params(axis='y',length=0,pad=7,labelsize=13.8);ax.spines[['top','right','left']].set_visible(False)
    ax.grid(axis='x',color='#DDE5E8',lw=.7)
    bx=fig.add_axes([.13,.14,.83,.29])
    for family,color,ls,label in [('ce_empirical',CE,'-','CE'),('er_binary',ER,'--','ER binary')]:
        g=mean_curves[mean_curves.family==family].sort_values('negative_fraction')
        assert len(g)==11
        by_input=curves[(curves.normalization=='own_radius')&(curves.metric=='NARMA10_test_nmse')&(curves.family==family)&(curves.input_scale!='ALL')]
        expected=by_input.groupby('negative_fraction')['mean'].mean().sort_index()
        np.testing.assert_allclose(g['mean'],expected,rtol=1e-12)
        bx.plot(g.negative_fraction*100,g['mean'],color=color,lw=2.2,ls=ls,marker='o',ms=3.5,label=label)
        bx.fill_between(g.negative_fraction*100,g.ci_low,g.ci_high,color=color,alpha=.12,lw=0)
    bx.set(xticks=[0,20,40,60,80,100],xlabel='Inhibitory edges (%)',ylabel='NMSE',ylim=(.115,.36),yticks=[.15,.20,.25,.30,.35]);clean(bx)
    bx.set_title('Mean error across all 24 settings',fontsize=13.5,pad=11);bx.tick_params(labelsize=12);bx.set_xlabel('Inhibitory edges (%)',fontsize=12);bx.set_ylabel('NMSE',fontsize=13)
    fig.legend(*bx.get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.53,0),frameon=False,ncol=2,fontsize=13)
    pd.DataFrame(rows).to_csv(DATA/'narma_auc.csv',index=False)
    save(fig,'poster_narma.png',dict(metric='NARMA10_test_nmse',normalization='own_radius',models=selected,
        top='all 24 settings; normal error AUC',bottom='two mean-error curves; equal average over all 24 input/radius/leak settings',
        source='archived paired NARMA10; no rerun',intervals='95% paired-realization bootstrap'))


def critics():
    d=table('architecture/performance_auc_per_realization.csv')
    fig,ax=plt.subplots(figsize=(7.15,3.35));fig.subplots_adjust(left=.13,right=.98,bottom=.27,top=.83)
    modes=['own_radius','fixed_reference','shared_ce_scale'];saved=[]
    weights=np.random.default_rng(20261122).multinomial(100,np.full(100,.01),size=1000)/100
    for family,color,label,offset in [('er_binary',ER,'ER binary',-.07),
                                     ('ws_binary',COLORS['ws_binary'],'WS-like binary',.07)]:
        means=[];low=[];high=[]
        for norm in modes:
            g=d[(d.metric=='MC_200')&(d.normalization==norm)].pivot(index='repeat_id',columns='family',values='performance_auc')
            assert len(g)==100
            gain=(g[family]-g['ce_binary']).to_numpy();means.append(gain.mean());ci=np.quantile(weights@gain,[.025,.975]);low.append(ci[0]);high.append(ci[1])
        mu=np.array(means);lo=np.array(low);hi=np.array(high);x=np.arange(3)+offset
        ax.errorbar(x,mu,yerr=[mu-lo,hi-mu],color=color,marker='o',ms=5,lw=1.7,capsize=3,label=label)
        saved.extend(dict(family=family,normalization=norm,advantage=mean,ci_low=l,ci_high=h) for norm,mean,l,h in zip(modes,mu,lo,hi))
    ax.axhline(0,color='.6',ls=':',lw=1);ax.set(xticks=range(3),xticklabels=['Own radius','Fixed ref.','Shared CE'],ylabel='MC200 AUC gain over CE binary',ylim=(-.65,5.2));clean(ax)
    ax.set_ylabel('MC AUC gain over CE binary',fontsize=13)
    ax.tick_params(axis='x',labelsize=13)
    fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.55,.99),ncol=2,frameon=False,fontsize=12.8)
    pd.DataFrame(saved).to_csv(DATA/'normalization_gaps.csv',index=False)
    save(fig,'poster_normalization_caveat.png',dict(metric='MC_200',reference='ce_binary',controls=['er_binary','ws_binary'],normalizations=modes,
        estimand='paired control-minus-CE-binary performance AUC; shared multiplier reverses CE/ER binary order',
        bootstrap=dict(draws=1000,seed=20261122,unit='whole paired realization')))


def main():
    OUT.mkdir(exist_ok=True);DATA.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'text.color':INK,'axes.labelcolor':INK,
        'axes.edgecolor':'#8B9BA5','axes.titlesize':16,'axes.labelsize':15,'xtick.labelsize':13,'ytick.labelsize':13,'axes.unicode_minus':False})
    sign_sweep();mc_curves();structure_auc();weight_auc();narma();critics()
    peaks=table('descriptive_peak_MC200.csv');peaks=peaks[(peaks.suite=='architecture')&(peaks.normalization=='own_radius')].sort_values('maximum_seed_mean_MC200',ascending=False)
    peaks.to_csv(DATA/'peak_mc200_ordering.csv',index=False)
    expected=['ws_binary','er_binary','ws_halfnormal','er_halfnormal','ws_signed_empirical','er_signed_empirical',
              'ce_binary','ce_halfnormal','ce_degree_rewired','ce_shuffled','ce_empirical','ce_unknown_removed']
    assert list(peaks.family)==expected
    auc=table('er/performance_auc.csv');own=auc[(auc.normalization=='own_radius')&(auc.input_scale=='ALL')]
    gamma=table('er/gamma_summary.csv');gamma=gamma[gamma.normalization=='own_radius']
    summary=[]
    for metric in ['MC_200','NARMA10_test_nmse']:
        a=own[own.metric==metric].set_index('family');g=gamma[gamma.metric==metric].iloc[0]
        summary.append(dict(metric=metric,empirical_auc=a.loc['empirical','performance_auc'],gamma_auc=a.loc['gamma','performance_auc'],
            advantage=g.gamma_advantage_auc,ci_low=g.ci_low,ci_high=g.ci_high,
            improvement_percent=100*g.gamma_advantage_auc/a.loc['empirical','performance_auc']))
    pd.DataFrame(summary).to_csv(DATA/'gamma_effect_summary.csv',index=False)
    manifest=dict(analysis=str(ANALYSIS.relative_to(ROOT)),experiment_id='49e6a1c836ec2a7286fa5599d1acecabb63fbe29e78228e167705fafe9f9474b',
        inputs=INPUTS,selections=SELECTIONS,figure_script_sha256=digest(Path(__file__)),
        data_source='MC200 run 274500; archived paired NARMA10; no simulations',
        bootstrap=dict(draws=1000,seed=20261122,unit='whole paired realization'),
        design_reference='Four user-provided camera sketches dated 2026-11-22',
        outputs={f:digest(OUT/f) for f in SELECTIONS},
        data_outputs={str(f.relative_to(HERE)):digest(f) for f in DATA.iterdir() if f.is_file() and f.name in ['edge_sign_schematic.json','sign_nesting_audit.json','mc_input_curves.csv','narma_mean_curves.csv','mc_auc_inset.csv','structural_mc_auc.csv','er_weight_mc_auc.csv','narma_auc.csv','normalization_gaps.csv','peak_mc200_ordering.csv','gamma_effect_summary.csv']})
    (HERE/'poster_sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Built {len(SELECTIONS)} poster figures with verified MC200 inputs.',flush=True)


if __name__=='__main__':main()

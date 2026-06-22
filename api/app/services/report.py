"""Builds a self-contained HTML report (cover + executive summary + per-domain).

Charts are rendered with ECharts using the **SVG renderer**, so when the HTML is
printed to PDF (via Playwright/headless Chromium) the charts stay vector — crisp
at any zoom, not a rasterized screenshot.
"""
from __future__ import annotations

import json
import os

from ..models import Assessment

_ECHARTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "echarts.min.js")


def _echarts_js() -> str:
    with open(_ECHARTS_PATH, encoding="utf-8") as f:
        return f.read()


_TEMPLATE = r"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"/>
<style>
  *{box-sizing:border-box} body{margin:0;background:#fff;font-family:system-ui,Segoe UI,Roboto,sans-serif;color:#0f172a}
  .page{padding:0} h1{font-size:22px;margin:0 0 4px} h2{font-size:15px;margin:22px 0 8px;color:#334155}
  .mut{color:#64748b;font-size:12px} .cover{border-bottom:3px solid #2563eb;padding-bottom:14px;margin-bottom:8px}
  .cover .dot{display:inline-block;width:18px;height:18px;border-radius:5px;background:#2563eb;vertical-align:-3px;margin-right:6px}
  table{width:100%;border-collapse:collapse;font-size:12px;margin-top:6px}
  th{text-align:left;color:#64748b;font-size:11px;font-weight:600;padding:6px 8px;border-bottom:1px solid #e2e8f0}
  td{padding:6px 8px;border-bottom:1px solid #eef2f7}
  .meta{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:10px}
  .meta div{font-size:12px} .meta b{display:block;color:#64748b;font-weight:600;font-size:11px}
  .grid2{display:grid;grid-template-columns:260px 1fr;gap:16px;align-items:center}
  .pill{display:inline-block;font-size:11px;font-weight:600;padding:2px 9px;border-radius:999px}
  .ec{width:100%}
</style></head><body><div class="page">
  <div class="cover">
    <h1><span class="dot"></span>Relatório de Maturidade de SOC</h1>
    <div class="mut">__FRAMEWORK__ · __NAME__</div>
    <div class="meta">
      <div><b>Cliente</b>__CLIENT__</div>
      <div><b>Responsável</b>__ASSESSOR__</div>
      <div><b>Data</b>__DATE__</div>
    </div>
  </div>

  <h2>Sumário executivo</h2>
  <div class="grid2">
    <div id="gauge" class="ec" style="height:200px"></div>
    <div>
      <div style="font-size:30px;font-weight:700" id="bignum"></div>
      <div id="biglevel"></div>
      <div class="mut" id="bigcov" style="margin-top:6px"></div>
    </div>
  </div>

  <h2>Ranking de domínios (0–5)</h2>
  <div id="rank" class="ec"></div>

  <h2>Radar por domínio (0–5)</h2>
  <div id="radar" class="ec" style="height:300px"></div>
  <div id="radarnote" class="mut" style="text-align:center;margin-top:4px"></div>

  <h2>Detalhamento por domínio</h2>
  <table><thead><tr><th>Domínio</th><th>Maturidade (0–5)</th><th>Nível</th><th>Meta</th><th>Cobertura</th></tr></thead>
  <tbody id="tbody"></tbody></table>

  <h2>Detalhe por domínio (subdomínios)</h2>
  <div id="subcharts"></div>
</div>
<script>__ECHARTS__</script>
<script>
var DASH = __DASH__;
var LEVEL=['Inexistente','Inicial','Limitado','Definido','Gerenciado','Otimizado'];
function band(s){if(s==null)return '#cbd5e1';if(s<1)return '#dc2626';if(s<2)return '#ea580c';if(s<3)return '#d97706';if(s<4)return '#65a30d';return '#16a34a';}
function bandSoft(s){if(s==null)return '#f1f5f9';if(s<1)return '#fee2e2';if(s<2)return '#ffedd5';if(s<3)return '#fef3c7';if(s<4)return '#ecfccb';return '#dcfce7';}
function bandText(s){if(s==null)return '#64748b';if(s<1)return '#991b1b';if(s<2)return '#9a3412';if(s<3)return '#854d0e';if(s<4)return '#3f6212';return '#166534';}
function lvl(s){return s==null?'não avaliado':LEVEL[Math.max(0,Math.min(5,Math.round(s)))];}
function f1(s){return s==null?'—':(Math.round(s*10)/10).toFixed(1);}
function p2s(p){return p==null?null:p/100*5;}

var overall=p2s(DASH.overall.normalized_pct), overallT=p2s(DASH.overall.target_pct);
var D=DASH.domains.map(function(d){return {key:d.label,score:p2s(d.normalized_pct),target:p2s(d.target_pct),answered:d.answered,total:d.total,assessed:d.answered>0};});

document.getElementById('bignum').textContent=(overall==null?'—':f1(overall))+' / 5';
document.getElementById('bignum').style.color=bandText(overall);
document.getElementById('biglevel').innerHTML='<span class="pill" style="background:'+bandSoft(overall)+';color:'+bandText(overall)+'">'+lvl(overall)+'</span>';
document.getElementById('bigcov').textContent=DASH.overall.answered+'/'+DASH.overall.total+' itens avaliados'+(overallT!=null?(' · meta '+f1(overallT)):'');

echarts.init(document.getElementById('gauge'),null,{renderer:'svg'}).setOption({animation:false,series:[{type:'gauge',min:0,max:5,splitNumber:5,radius:'92%',center:['50%','58%'],progress:{show:true,width:14,roundCap:true,itemStyle:{color:band(overall)}},axisLine:{lineStyle:{width:14,color:[[1,'#e5e7eb']]}},axisTick:{show:false},splitLine:{length:7,lineStyle:{color:'#cbd5e1'}},axisLabel:{fontSize:9,color:'#94a3b8',distance:12},pointer:{show:false},anchor:{show:false},detail:{valueAnimation:false,offsetCenter:[0,'-4%'],fontSize:28,fontWeight:'bolder',color:band(overall),formatter:function(){return overall==null?'—':f1(overall)}},data:[{value:overall==null?0:overall}],title:{show:false}}]});

var ranked=D.slice().sort(function(a,b){return (b.assessed-a.assessed)||((b.score||0)-(a.score||0))});
var rankEl=document.getElementById('rank'); rankEl.style.height=Math.max(160,ranked.length*28+30)+'px';
echarts.init(rankEl,null,{renderer:'svg'}).setOption({animation:false,grid:{left:8,right:46,top:6,bottom:22,containLabel:true},
  xAxis:{type:'value',min:0,max:5,interval:1,axisLabel:{color:'#94a3b8'},splitLine:{lineStyle:{color:'#eef2f7'}}},
  yAxis:{type:'category',inverse:true,data:ranked.map(function(d){return d.key}),axisTick:{show:false},axisLine:{show:false},axisLabel:{width:150,overflow:'break',color:'#334155',fontSize:11}},
  series:[{type:'bar',barWidth:12,data:ranked.map(function(d){return {value:d.assessed?d.score:0,itemStyle:{color:d.assessed?band(d.score):'#e2e8f0',borderRadius:[0,4,4,0]}}}),
    label:{show:true,position:'right',distance:6,fontSize:11,color:'#94a3b8',formatter:function(p){var d=ranked[p.dataIndex];return d.assessed?f1(d.score):'não avaliado'}},
    markLine:overall==null?undefined:{silent:true,symbol:'none',lineStyle:{color:'#0f172a',type:'dashed',width:1},data:[{xAxis:overall}],label:{formatter:'média '+f1(overall),position:'insideEndTop',fontSize:10,color:'#475569'}}},
   {type:'scatter',symbol:'rect',symbolSize:[3,14],silent:true,itemStyle:{color:'#0f172a'},data:ranked.map(function(d,i){return d.target!=null?[d.target,i]:null})}]});

var assessedD=D.filter(function(d){return d.assessed});
var naC=D.length-assessedD.length;
if(assessedD.length>=3){echarts.init(document.getElementById('radar'),null,{renderer:'svg'}).setOption({animation:false,tooltip:{},
  radar:{indicator:assessedD.map(function(d){return {name:d.key,max:5}}),radius:'64%',center:['50%','52%'],splitNumber:5,axisName:{color:'#475569',fontSize:10},splitLine:{lineStyle:{color:'#e5e7eb'}},splitArea:{show:false},axisLine:{lineStyle:{color:'#e5e7eb'}}},
  series:[{type:'radar',symbolSize:3,data:[{value:assessedD.map(function(d){return d.score}),name:'Maturidade',areaStyle:{color:'rgba(37,99,235,.15)'},lineStyle:{color:'#2563eb',width:2},itemStyle:{color:'#2563eb'}}]}]});
  if(naC>0)document.getElementById('radarnote').textContent=naC+' domínio(s) não avaliado(s) fora do radar';
}else{document.getElementById('radar').style.display='none';document.getElementById('radarnote').textContent='Radar disponível a partir de 3 domínios avaliados.';}

document.getElementById('tbody').innerHTML=D.map(function(d){return '<tr><td><b>'+d.key+'</b></td><td>'+(d.assessed?f1(d.score):'—')+
  '</td><td><span class="pill" style="background:'+bandSoft(d.assessed?d.score:null)+';color:'+bandText(d.assessed?d.score:null)+'">'+(d.assessed?lvl(d.score):'não avaliado')+
  '</span></td><td>'+(d.target!=null?f1(d.target):'—')+'</td><td>'+d.answered+'/'+d.total+'</td></tr>'}).join('');

// per-domain subdomain bars (mirrors the on-screen detail so the PDF carries both views)
var subWrap=document.getElementById('subcharts');
D.forEach(function(d,di){
  if(!d.assessed)return;
  var ctrls=(DASH.domains[di].controls)||[];
  if(!ctrls.length)return;
  var h=document.createElement('div');h.textContent=d.key+' — '+f1(d.score)+' · '+lvl(d.score);
  h.style.cssText='font-size:13px;font-weight:600;margin:14px 0 2px;color:#334155';
  var div=document.createElement('div');div.style.height=Math.max(110,ctrls.length*22+30)+'px';
  subWrap.appendChild(h);subWrap.appendChild(div);
  var items=ctrls.map(function(c){return {name:c.label,score:p2s(c.normalized_pct),assessed:c.answered>0}})
    .sort(function(a,b){return ((b.assessed?1:0)-(a.assessed?1:0))||((b.score||0)-(a.score||0))});
  echarts.init(div,null,{renderer:'svg'}).setOption({animation:false,grid:{left:8,right:50,top:6,bottom:20,containLabel:true},
    xAxis:{type:'value',min:0,max:5,interval:1,axisLabel:{color:'#94a3b8'},splitLine:{lineStyle:{color:'#eef2f7'}}},
    yAxis:{type:'category',inverse:true,data:items.map(function(i){return i.name}),axisTick:{show:false},axisLine:{show:false},axisLabel:{width:150,overflow:'break',color:'#334155',fontSize:10}},
    series:[{type:'bar',barWidth:10,data:items.map(function(i){return {value:i.assessed?i.score:0,itemStyle:{color:i.assessed?band(i.score):'#e2e8f0',borderRadius:[0,3,3,0]}}}),
      label:{show:true,position:'right',distance:5,fontSize:10,color:'#94a3b8',formatter:function(p){var i=items[p.dataIndex];return i.assessed?f1(i.score):'n/a'}},
      markLine:d.score==null?undefined:{silent:true,symbol:'none',lineStyle:{color:'#0f172a',type:'dashed',width:1},data:[{xAxis:d.score}]}}]});
});
window.__READY__=true;
</script></body></html>"""


def build_report_html(assessment: Assessment, framework_name: str, dash: dict) -> str:
    return (
        _TEMPLATE.replace("__ECHARTS__", _echarts_js())
        .replace("__DASH__", json.dumps(dash, ensure_ascii=False).replace("</", "<\\/"))
        .replace("__FRAMEWORK__", framework_name or "")
        .replace("__NAME__", assessment.name or "")
        .replace("__CLIENT__", assessment.client or "—")
        .replace("__ASSESSOR__", assessment.assessor or "—")
        .replace("__DATE__", assessment.created_at.strftime("%d/%m/%Y") if assessment.created_at else "—")
    )

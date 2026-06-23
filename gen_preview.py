# -*- coding: utf-8 -*-
"""Generates the full single-file app (preview.html) with SOC-CMM fidelity."""
import json, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "assets", "frameworks.json"), encoding="utf-8") as f:
    data_json = f.read()

TEMPLATE = r"""<!doctype html><html lang="pt-BR"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Viaconnect SOC Maturity</title>
<style>
  :root{--bg:#f1f5f9;--card:#fff;--fg:#0f172a;--mut:#64748b;--border:#e2e8f0;--primary:#2563eb;--cap:#7c3aed;--green:#059669;--amber:#d97706;--red:#dc2626;--radius:12px}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);font-family:system-ui,Segoe UI,Roboto,sans-serif}
  a{color:var(--primary);cursor:pointer}
  header{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.92);backdrop-filter:blur(6px);border-bottom:1px solid var(--border)}
  .bar{max-width:1240px;margin:0 auto;display:flex;align-items:center;gap:18px;height:56px;padding:0 18px}
  .logo{display:flex;align-items:center;gap:8px;font-weight:700}
  .logo .dot{width:22px;height:22px;border-radius:6px;background:var(--primary)}
  nav{display:flex;gap:4px}
  nav button{border:0;background:transparent;color:var(--mut);font:inherit;font-weight:600;padding:7px 12px;border-radius:8px;cursor:pointer;font-size:14px}
  nav button.active{background:rgba(37,99,235,.1);color:var(--primary)}
  .right{margin-left:auto;display:flex;align-items:center;gap:12px;font-size:14px;color:var(--mut)}
  main{max-width:1240px;margin:0 auto;padding:22px 18px}
  h1{font-size:22px;margin:0 0 2px} h2{font-size:17px;margin:20px 0 10px}
  .sub{color:var(--mut);font-size:14px;margin:0 0 18px}
  .card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);box-shadow:0 1px 2px rgba(0,0,0,.04);margin-bottom:16px}
  .card h3{margin:0;padding:14px 16px;font-size:14px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:8px}
  .pad{padding:16px}
  .grid{display:grid;gap:16px}
  .badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 9px;border-radius:999px;background:#eef2f7;color:var(--mut)}
  .badge.b{background:rgba(37,99,235,.1);color:var(--primary)} .badge.g{background:#d1fae5;color:#047857}
  .badge.a{background:#fef3c7;color:#b45309} .badge.p{background:#ede9fe;color:#6d28d9}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th{text-align:left;color:var(--mut);font-size:12px;font-weight:600;padding:8px 10px;border-bottom:1px solid var(--border)}
  td{padding:9px 10px;border-bottom:1px solid var(--border)} tr:last-child td{border-bottom:0}
  select,input,textarea{font:inherit;font-size:13px;padding:8px 9px;border:1px solid var(--border);border-radius:8px;background:#fff;width:100%}
  input[type=checkbox],input[type=radio]{width:auto;padding:0;cursor:pointer}
  label.f{font-size:11px;font-weight:600;color:var(--mut);display:block;margin-bottom:3px}
  .btn{border:0;background:var(--primary);color:#fff;font:inherit;font-weight:600;padding:8px 14px;border-radius:8px;cursor:pointer;font-size:14px}
  .btn:disabled{opacity:.5;cursor:default}
  .btn.ghost{background:#fff;color:var(--fg);border:1px solid var(--border)}
  .btn.sm{padding:5px 10px;font-size:13px} .btn.danger{background:#fff;color:var(--red);border:1px solid #fecaca}
  .row{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap} .mini{font-size:12px;color:var(--mut)}
  .qrow{border-top:1px solid var(--border);padding:12px 0;display:grid;grid-template-columns:1fr 360px;gap:14px;align-items:start}
  .qrow:first-child{border-top:0}
  .qcode{font-size:12px;font-weight:700;color:var(--primary);display:flex;gap:6px;align-items:center}
  .qtype{font-size:10px;font-weight:700;padding:1px 6px;border-radius:4px}
  .qtype.M{background:rgba(37,99,235,.1);color:var(--primary)} .qtype.C{background:#ede9fe;color:var(--cap)}
  .qtext{font-size:14px;margin:3px 0}
  .qremark{font-size:12px;color:var(--mut);margin-top:4px}
  .help-btn{width:18px;height:18px;border-radius:50%;border:1px solid var(--border);background:#fff;color:var(--primary);font-weight:700;font-size:11px;cursor:pointer;line-height:1}
  .navsel{display:grid;grid-template-columns:1fr 1.4fr auto auto;gap:10px;align-items:end;margin-bottom:14px}
  .overlay{position:fixed;inset:0;background:rgba(15,23,42,.45);z-index:50;display:flex;align-items:center;justify-content:center;padding:20px}
  .modal{background:#fff;border-radius:14px;max-width:580px;width:100%;max-height:86vh;overflow:auto;box-shadow:0 20px 60px rgba(0,0,0,.3)}
  .modal .mh{padding:16px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px}
  .modal .mb{padding:18px}
  .lvl{display:flex;gap:10px;padding:7px 9px;border-radius:8px;font-size:13px;align-items:flex-start}
  .lvl b{flex:0 0 22px;color:var(--primary)} .lvl.sel{background:rgba(37,99,235,.08);outline:1px solid rgba(37,99,235,.3)}
  .empty{padding:40px;text-align:center;color:var(--mut)}
  .lgi{cursor:pointer;padding:1px 4px;border-radius:5px} .lgi:hover{background:#eef2f7}
  .domhead{display:flex;align-items:center;gap:10px;cursor:pointer;user-select:none;padding:12px 16px}
  .domhead:hover{background:#f8fafc} .chev{transition:transform .15s;color:var(--mut)} .chev.open{transform:rotate(90deg)}
  text{font-family:system-ui,sans-serif}
  /* dashboard refactor */
  .dgrid{display:grid;gap:16px}
  .kpi{background:#f8fafc;border:1px solid var(--border);border-radius:10px;padding:11px 13px}
  .kpi .k{font-size:12px;color:var(--mut)} .kpi .v{font-size:20px;font-weight:600;margin-top:2px}
  .scard{border:1px solid var(--border);border-radius:10px;padding:12px}
  .scard.na{border-style:dashed;opacity:.85}
  .seg{display:flex;gap:3px;margin-top:8px} .seg span{flex:1;height:6px;border-radius:2px;background:var(--border)}
  .lvlpill{display:inline-block;font-size:11px;font-weight:600;padding:2px 9px;border-radius:999px}
  .tabbar{display:flex;gap:2px;border-bottom:1px solid var(--border);margin:12px 0 16px;flex-wrap:wrap}
  .tabbar button{border:0;background:transparent;font:inherit;font-weight:600;font-size:14px;color:var(--mut);padding:9px 15px;cursor:pointer;border-bottom:2px solid transparent}
  .tabbar button.on{color:var(--primary);border-bottom-color:var(--primary)}
  .hz{border:1px solid var(--border);border-radius:10px;padding:12px;background:#fff}
  .hz h4{margin:0 0 8px;font-size:13px}
  .act{border:1px solid var(--border);border-radius:8px;padding:9px 10px;margin-bottom:8px;background:#f8fafc}
  .segsel{display:inline-flex;gap:4px;flex-wrap:wrap}
  .segbtn{min-width:30px;height:30px;border:1px solid var(--border);background:#fff;color:var(--mut);font:inherit;font-weight:700;font-size:13px;border-radius:7px;cursor:pointer;padding:0 8px}
  .segbtn:hover{border-color:var(--primary)}
  .seglbl{font-size:12px;color:#334155;margin-top:5px;min-height:15px}
  .navrail{position:sticky;top:64px;align-self:start;max-height:calc(100vh - 80px);overflow:auto}
  .navd{border-radius:8px;margin-bottom:3px}
  .navd>button{width:100%;text-align:left;border:0;background:transparent;font:inherit;font-size:13px;font-weight:600;color:#334155;padding:7px 9px;cursor:pointer;display:flex;align-items:center;gap:8px;border-radius:8px}
  .navd>button.on{background:rgba(37,99,235,.1);color:var(--primary)}
  .navd .pbar{flex:1;height:4px;background:#eef2f7;border-radius:2px;overflow:hidden}
  .navd .pbar i{display:block;height:4px;background:#2563eb}
  .navasp{border:0;background:transparent;font:inherit;font-size:12px;color:var(--mut);padding:4px 9px 4px 26px;cursor:pointer;display:block;width:100%;text-align:left;border-radius:6px}
  .navasp.on{background:#f1f5f9;color:var(--fg);font-weight:600}
  .tierp{font-size:10px;font-weight:700;padding:1px 6px;border-radius:4px}
  .tierp.Standard{background:#e0f2fe;color:#075985}.tierp.Advanced{background:#ede9fe;color:#6d28d9}.tierp.Processo{background:#f1f5f9;color:#475569}.tierp.Futuro{background:#fef3c7;color:#854d0e}
  .toggle{display:inline-flex;border:1px solid var(--border);border-radius:8px;overflow:hidden;margin-left:auto}
  .toggle button{border:0;background:#fff;font:inherit;font-size:12px;font-weight:600;color:var(--mut);padding:5px 11px;cursor:pointer}
  .toggle button.on{background:var(--primary);color:#fff}
  /* recommendations + roadmap polish */
  .chip{border:1px solid var(--border);background:#fff;color:#475569;font:inherit;font-weight:600;font-size:12px;padding:5px 11px;border-radius:999px;cursor:pointer;white-space:nowrap;flex:0 0 auto}
  .chip:hover{border-color:var(--primary)}
  .chip.on{background:#dcfce7;border-color:#86efac;color:#166534}
  .hchip{display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;border-radius:999px}
  .segp{display:inline-flex;border:1px solid var(--border);border-radius:8px;overflow:hidden;flex:0 0 auto}
  .segp button{border:0;border-left:1px solid var(--border);background:#fff;font:inherit;font-size:12px;font-weight:600;color:var(--mut);padding:5px 11px;cursor:pointer}
  .segp button:first-child{border-left:0}
  .segp button.on.alta{background:#fee2e2;color:#991b1b}
  .segp button.on.media{background:#fef3c7;color:#854d0e}
  .segp button.on.baixa{background:#dcfce7;color:#166534}
  .segp button:disabled{opacity:.45;cursor:default}
  .prirow{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:10px 0;border-top:1px solid var(--border)}
  .prirow:first-child{border-top:0}
  .dgrid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start}
  @media(max-width:880px){.dgrid3{grid-template-columns:1fr}}
  .hzh{display:flex;align-items:center;gap:8px;margin:0 0 10px}
  .hdot{width:9px;height:9px;border-radius:50%;flex:0 0 auto}
  .spin{width:20px;height:20px;border:3px solid #e2e8f0;border-top-color:var(--primary);border-radius:50%;animation:spin .8s linear infinite;flex:0 0 auto}
  @keyframes spin{to{transform:rotate(360deg)}}
  .skel{background:linear-gradient(90deg,#eef2f7 25%,#e2e8f0 37%,#eef2f7 63%);background-size:400% 100%;animation:sk 1.3s ease infinite;border-radius:8px}
  @keyframes sk{0%{background-position:100% 0}100%{background-position:-100% 0}}
  .ec{width:100%}
  @media print{header,.no-print{display:none!important}main{max-width:none;padding:0}.card{break-inside:avoid;box-shadow:none}.domdetail{display:block!important}}
</style></head><body>
<div id="root"></div><div id="modal-root"></div>
<script>__ECHARTS__</script>
<script>
const DATA = __DATA__;
const VIA = DATA.viaconnect;
const SOC = DATA.soc;
const FRAMEWORKS=[
  Object.assign({}, VIA, {opts:{importance:false,capability:false,target:true}}),
  {slug:'soc-cmm-basic',name:'SOC-CMM 2.4.2 — Basic',kind:'soc-cmm',scaleNote:'Maturidade SOC-CMM 0–5',domains:SOC.domains,opts:{importance:false,capability:true,target:false}},
  {slug:'soc-cmm-advanced',name:'SOC-CMM 2.4.2 — Advanced',kind:'soc-cmm',scaleNote:'Maturidade + Importância + Capability',domains:SOC.domains,opts:{importance:true,capability:true,target:false}},
];
const FW={}; FRAMEWORKS.forEach(f=>FW[f.slug]=f);
const FACTOR={1:0,2:0.5,3:1,4:2,5:4};
const IMP_LABEL={1:'None',2:'Low',3:'Normal',4:'High',5:'Critical'};

// ===== persistence =====
// Persistência: backend (PostgreSQL via /api/state) quando disponível; localStorage
// como cache e fallback (abrir o preview.html solto continua funcionando offline).
// A config do Claude (db.claude, inclui a chave) fica SÓ no navegador, nunca no backend.
const LS="soc_app_db_v3";
let BACKEND=true;
function freshDB(){return {users:[{id:1,username:"admin",password:"admin",name:"Administrador",role:"admin"}],orgs:[],assessments:[],answers:{},session:null,seq:1};}
function loadLocal(){try{return JSON.parse(localStorage.getItem(LS))||freshDB()}catch(e){return freshDB()}}
function persistLocal(){try{localStorage.setItem(LS,JSON.stringify(db))}catch(e){}}
let _saveTimer=null;
function save(){
  persistLocal();
  if(!BACKEND)return;
  clearTimeout(_saveTimer);
  _saveTimer=setTimeout(function(){
    const payload=Object.assign({},db);delete payload.claude; // chave do Claude não vai pro banco
    fetch('/api/state',{method:'PUT',headers:{'content-type':'application/json'},body:JSON.stringify(payload)}).catch(function(){});
  },400);
}
let db=loadLocal();
function nid(){db.seq=(db.seq||1)+1;return db.seq}
const state={view:db.session?"orgs":"login",orgId:null,assessmentId:null,dIdx:0,aIdx:0,openDomains:{},orgTab:'assessment'};
function curUser(){return db.users.find(u=>u.username===db.session)||null}

// ===== scoring (SOC-CMM formula transcription) =====
function mean(a){return a.length?a.reduce((x,y)=>x+y,0)/a.length:null}
function ans(aid){return db.answers[aid]||{}}
function impOf(q,a){return (a&&a.imp)||q.importance||3}
function socPct(qs,A,type){ // K% = max(0,100*(ΣI-ΣH)/(ΣJ-ΣH)); unanswered=0
  let H=0,I=0,has=false,any=false;
  qs.forEach(q=>{if(q.type!==type)return;has=true;const a=A[q.code];const f=FACTOR[impOf(q,a)];
    H+=f;if(a&&a.cur!=null){I+=a.cur*f;any=true;}});
  if(!has||H===0)return null;if(!any)return 0;return Math.max(0,100*(I-H)/(5*H-H));
}
function simplePct(qs,A){const v=[];qs.forEach(q=>{const a=A[q.code];if(a&&a.cur!=null)v.push(a.cur/q.scaleMax*100)});return mean(v);}
function countAns(qs,A){let n=0;qs.forEach(q=>{const a=A[q.code];if(a&&a.cur!=null)n++});return n;}
function aspectScore(fw,asp,A){
  const isSoc=fw.kind==='soc-cmm';
  const matQ=asp.questions.filter(q=>q.type==='M'), capQ=asp.questions.filter(q=>q.type==='C');
  const mpct= isSoc? socPct(asp.questions,A,'M') : simplePct(asp.questions,A);
  const cpct= (isSoc&&asp.hasCapability)? socPct(asp.questions,A,'C') : null;
  // target (viaconnect only)
  let tpct=null; if(fw.opts.target){const v=[];asp.questions.forEach(q=>{const a=A[q.code];if(a&&a.tgt!=null)v.push(a.tgt/q.scaleMax*100)});tpct=mean(v);}
  const smax= isSoc?5:(asp.questions[0]?asp.questions[0].scaleMax:5);
  return {code:asp.code,name:asp.name,hasCapability:!!asp.hasCapability,
    mpct,cpct,tpct,
    matScore: mpct==null?null:5*mpct/100,
    capScore: cpct==null?null:3*cpct/100,
    answered:countAns(asp.questions,A),total:asp.questions.length,
    rawMat: isSoc? (mpct==null?null:5*mpct/100) : (function(){const v=[];matQ.forEach(q=>{const a=A[q.code];if(a&&a.cur!=null)v.push(a.cur)});return mean(v)})()};
}
function domainScore(fw,d,A){
  const aspects=d.aspects.map(a=>aspectScore(fw,a,A));
  const mp=aspects.map(a=>a.mpct).filter(x=>x!=null);
  const cp=aspects.filter(a=>a.hasCapability).map(a=>a.cpct).filter(x=>x!=null);
  const tp=aspects.map(a=>a.tpct).filter(x=>x!=null);
  return {key:d.key,name:d.name,aspects,mpct:mean(mp),cpct:cp.length?mean(cp):null,tpct:tp.length?mean(tp):null,
    answered:aspects.reduce((s,a)=>s+a.answered,0),total:aspects.reduce((s,a)=>s+a.total,0),
    hasCapability:aspects.some(a=>a.hasCapability)};
}
function dashboard(fw,A){
  const domains=fw.domains.map(d=>domainScore(fw,d,A));
  const mp=domains.map(d=>d.mpct).filter(x=>x!=null);
  const cp=domains.map(d=>d.cpct).filter(x=>x!=null);
  const tp=domains.map(d=>d.tpct).filter(x=>x!=null);
  return {domains,overall:mean(mp),overallCap:cp.length?mean(cp):null,overallTarget:tp.length?mean(tp):null,
    answered:domains.reduce((s,d)=>s+d.answered,0),total:domains.reduce((s,d)=>s+d.total,0)};
}
const col=p=>p==null?'#94a3b8':p>=80?'#059669':p>=60?'#2563eb':p>=40?'#d97706':'#dc2626';
const DOMCOL={Business:'#2563eb',People:'#0891b2',Process:'#7c3aed',Technology:'#d97706',Services:'#059669'};

// ===== maturity scale (0–5): accessible red→amber→green bands =====
const LEVELNAME=['Inexistente','Inicial','Limitado','Definido','Gerenciado','Otimizado'];
function band(s){ // s in 0..5 (or null)
  if(s==null)return '#cbd5e1';
  if(s<1)return '#dc2626'; if(s<2)return '#ea580c'; if(s<3)return '#d97706'; if(s<4)return '#65a30d'; return '#16a34a';
}
function bandSoft(s){if(s==null)return '#f1f5f9';
  if(s<1)return '#fee2e2'; if(s<2)return '#ffedd5'; if(s<3)return '#fef3c7'; if(s<4)return '#ecfccb'; return '#dcfce7';}
function bandText(s){if(s==null)return '#64748b';
  if(s<1)return '#991b1b'; if(s<2)return '#9a3412'; if(s<3)return '#854d0e'; if(s<4)return '#3f6212'; return '#166534';}
function levelName(s){return s==null?'não avaliado':LEVELNAME[Math.max(0,Math.min(5,Math.round(s)))];}
function fmt1(s){return s==null?'—':(Math.round(s*10)/10).toFixed(1);}

// ===== ECharts registry: render after innerHTML is set =====
const ECINST={}; let ECPENDING=[];
function ec(id,height,option){ECPENDING.push({id,option});return `<div id="${id}" class="ec" style="height:${height}px"></div>`;}
function flushCharts(){
  ECPENDING.forEach(c=>{const el=document.getElementById(c.id);if(!el)return;
    if(ECINST[c.id]){try{ECINST[c.id].dispose()}catch(e){}}
    const inst=echarts.init(el,null,{renderer:'svg'});inst.setOption(c.option);ECINST[c.id]=inst;});
  ECPENDING=[];
}
let _ecResize=false;
function ensureResize(){if(_ecResize)return;_ecResize=true;
  window.addEventListener('resize',()=>{Object.values(ECINST).forEach(i=>{try{i.resize()}catch(e){}})});}

// label wrap for radar axis names (no mid-word cut; full name in tooltip)
function wrapLabel(s,wid){s=String(s);const words=s.split(' ');let lines=[],cur='';
  words.forEach(w=>{if((cur+' '+w).trim().length>(wid||14)){if(cur)lines.push(cur);cur=w;}else{cur=(cur?cur+' ':'')+w;}});
  if(cur)lines.push(cur);if(lines.length>3){lines=lines.slice(0,3);lines[2]+='…';}return lines.join('\n');}

// --- chart options ---
function ecGauge(score,target){return {series:[{type:'gauge',min:0,max:5,splitNumber:5,radius:'94%',center:['50%','60%'],
  progress:{show:true,width:13,roundCap:true,itemStyle:{color:band(score)}},
  axisLine:{lineStyle:{width:13,color:[[1,'#e5e7eb']]}},axisTick:{show:false},
  splitLine:{length:7,lineStyle:{color:'#cbd5e1',width:1}},axisLabel:{fontSize:9,color:'#94a3b8',distance:11},
  pointer:{show:false},anchor:{show:false},
  detail:{valueAnimation:false,offsetCenter:[0,'-6%'],fontSize:30,fontWeight:'bolder',color:band(score),
    formatter:()=>score==null?'—':fmt1(score)},
  data:[{value:score==null?0:score}],title:{show:false}}]};}

function ecRanking(items,avg){ // items:[{name,score,target,assessed}] (already in display order; inverse keeps highest on top)
  const cats=items.map(x=>x.name);
  return {grid:{left:8,right:48,top:6,bottom:22,containLabel:true},
    tooltip:{trigger:'axis',axisPointer:{type:'shadow'},
      formatter:p=>{const it=items[p[0].dataIndex];return it.assessed?`${esc(it.full||it.name)}<br/><b>${fmt1(it.score)}</b> / 5 · ${levelName(it.score)}${it.target!=null?` · meta ${fmt1(it.target)}`:''}`:`${esc(it.full||it.name)}<br/>não avaliado`;}},
    xAxis:{type:'value',min:0,max:5,interval:1,axisLabel:{color:'#94a3b8'},splitLine:{lineStyle:{color:'#eef2f7'}}},
    yAxis:{type:'category',data:cats,inverse:true,axisTick:{show:false},axisLine:{show:false},
      axisLabel:{width:150,overflow:'break',color:'#334155',fontSize:11,lineHeight:13}},
    series:[
      {type:'bar',barWidth:13,z:2,data:items.map(it=>({value:it.assessed?it.score:0,
        itemStyle:{color:it.assessed?band(it.score):'#e2e8f0',borderRadius:[0,4,4,0]}})),
       label:{show:true,position:'right',distance:6,fontSize:11,color:'#94a3b8',
         formatter:p=>{const it=items[p.dataIndex];return it.assessed?fmt1(it.score):'não avaliado';}},
       markLine:avg==null?undefined:{silent:true,symbol:'none',lineStyle:{color:'#0f172a',type:'dashed',width:1},data:[{xAxis:avg}],label:{formatter:'média '+fmt1(avg),position:'insideEndTop',fontSize:10,color:'#475569'}}},
      {type:'scatter',symbol:'rect',symbolSize:[3,15],z:3,silent:true,itemStyle:{color:'#0f172a'},
       data:items.map((it,i)=>it.target!=null?[it.target,i]:null)}
    ]};
}

function ecRadar(items,withCap){ // items assessed-only:[{name,score,cap}]
  const ind=items.map(x=>({name:x.name,max:5}));
  const series=[{type:'radar',symbolSize:3,
    data:[{value:items.map(x=>x.score),name:'Maturidade',areaStyle:{color:'rgba(37,99,235,.15)'},lineStyle:{color:'#2563eb',width:2},itemStyle:{color:'#2563eb'}}]}];
  if(withCap)series[0].data.push({value:items.map(x=>x.cap==null?null:x.cap/3*5),name:'Capability',areaStyle:{color:'rgba(124,58,237,.08)'},lineStyle:{color:'#7c3aed',width:1.5,type:'dashed'},itemStyle:{color:'#7c3aed'}});
  return {tooltip:{trigger:'item',confine:true,formatter:()=>items.map(x=>`<div style="display:flex;justify-content:space-between;gap:14px"><span>${esc(x.full||x.name)}</span><b>${x.score==null?'—':fmt1(x.score)+' · '+levelName(x.score)}</b></div>`).join('')},legend:{bottom:0,itemWidth:14,textStyle:{fontSize:11,color:'#475569'}},
    radar:{indicator:ind,radius:'66%',center:['50%','48%'],splitNumber:5,
      axisName:{color:'#475569',fontSize:10,formatter:v=>wrapLabel(v,13)},
      splitLine:{lineStyle:{color:'#e5e7eb'}},splitArea:{show:false},axisLine:{lineStyle:{color:'#e5e7eb'}}},
    series};
}

function ecEvolution(points){ // [{label,score}]
  return {grid:{left:30,right:20,top:14,bottom:24},
    tooltip:{trigger:'axis',formatter:p=>`${esc(p[0].axisValue)}<br/><b>${fmt1(p[0].data)}</b> / 5`},
    xAxis:{type:'category',data:points.map(p=>p.label),axisLabel:{color:'#64748b',fontSize:11},axisLine:{lineStyle:{color:'#e5e7eb'}}},
    yAxis:{type:'value',min:0,max:5,interval:1,axisLabel:{color:'#94a3b8'},splitLine:{lineStyle:{color:'#eef2f7'}}},
    series:[{type:'line',smooth:true,symbolSize:7,data:points.map(p=>p.score),
      lineStyle:{color:'#2563eb',width:2.5},itemStyle:{color:'#2563eb'},areaStyle:{color:'rgba(37,99,235,.08)'},
      label:{show:true,formatter:p=>fmt1(p.data),color:'#2563eb',fontSize:11,position:'top'}}]};
}

// short code for a subdomain axis: part before "·" (e.g. "PROGRAM"), else the full name
function shortOrFull(name){const i=String(name).indexOf('·');return i>0?String(name).slice(0,i).trim():String(name);}
// per-domain SUBDOMAIN radar — short code on axis, full name+value+level in tooltip, no values on axis
function ecSubRadar(views,accent){
  const a=views.filter(v=>v.assessed);
  const ind=a.map(v=>({name:shortOrFull(v.full),max:5}));
  return {tooltip:{trigger:'item',confine:true,
      formatter:()=>a.map(v=>`<div style="display:flex;justify-content:space-between;gap:16px"><span>${esc(v.full)}</span><b>${fmt1(v.score)} · ${levelName(v.score)}</b></div>`).join('')},
    radar:{indicator:ind,radius:'60%',center:['50%','52%'],splitNumber:5,
      axisName:{color:'#475569',fontSize:10,formatter:v=>wrapLabel(v,12)},
      splitLine:{lineStyle:{color:'#e5e7eb'}},splitArea:{show:false},axisLine:{lineStyle:{color:'#e5e7eb'}}},
    series:[{type:'radar',symbolSize:3,data:[{value:a.map(v=>v.score),name:'Maturidade',
      areaStyle:{color:accent,opacity:0.12},lineStyle:{color:accent,width:2},itemStyle:{color:accent}}]}]};
}
// per-domain SUBDOMAIN bars — full names (wrap, no truncate), sorted, value+level, domain-average reference line
function ecSubBars(views,domAvg){
  const s=views.slice().sort((x,y)=>((y.assessed?1:0)-(x.assessed?1:0))||((y.score||0)-(x.score||0)));
  return {grid:{left:8,right:54,top:8,bottom:24,containLabel:true},
    tooltip:{trigger:'axis',axisPointer:{type:'shadow'},confine:true,
      formatter:p=>{const v=s[p[0].dataIndex];return v.assessed?`${esc(v.full)}<br/><b>${fmt1(v.score)}</b> / 5 · ${levelName(v.score)}`:`${esc(v.full)}<br/>não avaliado`;}},
    xAxis:{type:'value',min:0,max:5,interval:1,axisLabel:{color:'#94a3b8'},splitLine:{lineStyle:{color:'#eef2f7'}}},
    yAxis:{type:'category',inverse:true,data:s.map(v=>v.full),axisTick:{show:false},axisLine:{show:false},
      axisLabel:{width:160,overflow:'break',color:'#334155',fontSize:11,lineHeight:13}},
    series:[{type:'bar',barWidth:12,data:s.map(v=>({value:v.assessed?v.score:0,
        itemStyle:{color:v.assessed?band(v.score):'#e2e8f0',borderRadius:[0,4,4,0]}})),
      label:{show:true,position:'right',distance:6,fontSize:11,color:'#94a3b8',
        formatter:p=>{const v=s[p.dataIndex];return v.assessed?fmt1(v.score):'não avaliado';}},
      markLine:domAvg==null?undefined:{silent:true,symbol:'none',lineStyle:{color:'#0f172a',type:'dashed',width:1},data:[{xAxis:domAvg}],label:{formatter:'média '+fmt1(domAvg),position:'insideEndTop',fontSize:10,color:'#475569'}}}]};
}

// ===== charts =====
function gauge(pct,sub,subval){
  const v=Math.max(0,Math.min(100,pct||0)),r=70,c=2*Math.PI*r,dash=v/100*c,color=col(pct);
  return `<svg viewBox="0 0 200 200" width="200" height="200">
    <circle cx="100" cy="100" r="${r}" fill="none" stroke="#e2e8f0" stroke-width="22"/>
    <circle cx="100" cy="100" r="${r}" fill="none" stroke="${color}" stroke-width="22" stroke-dasharray="${dash} ${c}" stroke-linecap="round" transform="rotate(-90 100 100)"/>
    <text x="100" y="94" text-anchor="middle" font-size="34" font-weight="700" fill="${color}">${pct==null?'—':Math.round(v)+'%'}</text>
    <text x="100" y="116" text-anchor="middle" font-size="11" fill="#64748b">maturidade geral</text>
    ${sub!=null?`<text x="100" y="134" text-anchor="middle" font-size="11" fill="#7c3aed">${sub} ${subval}</text>`:''}
  </svg>`;
}
// shared legend row under any chart
function legendRow(items){return `<div style="display:flex;gap:18px;flex-wrap:wrap;justify-content:center;margin-top:8px">`+
  items.map(it=>`<span style="display:inline-flex;align-items:center;gap:6px;font-size:12px;color:#475569"><span style="width:16px;border-top:3px ${it.dash?'dashed':'solid'} ${it.c};display:inline-block"></span>${esc(it.label)}</span>`).join('')+`</div>`;}
// SOC-CMM radar — faithful to the official xlsx print: full aspect names around a
// 0–5 spider grid (0.5 steps), domains bracketed at the corners, legend at right.
function socRadar(domains){
  const spokes=[];const spans=[];let idx=0;
  domains.forEach(d=>{const start=idx;d.aspects.forEach((a,j)=>{spokes.push({dom:d.key,n:j+1,name:a.name,mat:a.matScore,cap:a.capScore,hasCap:a.hasCapability});idx++;});spans.push({key:d.key,start,end:idx-1});});
  const N=spokes.length,W=980,Hh=660,cx=455,cy=325,R=250,MAX=5,step=2*Math.PI/N,BC='#2f6fb3';
  const ang=i=>-Math.PI/2+i*step, pt=(i,v)=>[cx+Math.cos(ang(i))*R*(v||0)/MAX,cy+Math.sin(ang(i))*R*(v||0)/MAX];
  let g='';
  // spider grid: rings every 0.5
  for(let k=1;k<=10;k++){const rr=R*k/10;g+=`<polygon points="${spokes.map((_,i)=>{const a=ang(i);return [cx+Math.cos(a)*rr,cy+Math.sin(a)*rr].join(',')}).join(' ')}" fill="none" stroke="#dadfe6" stroke-width="0.7"/>`;}
  spokes.forEach((s,i)=>{const e=pt(i,5);g+=`<line id="rax-${i}" data-c="${DOMCOL[s.dom]}" x1="${cx}" y1="${cy}" x2="${e[0]}" y2="${e[1]}" stroke="#dadfe6" stroke-width="0.7"/>`;});
  // vertical axis scale 0..5 (0.5 steps) on the top spoke
  for(let k=0;k<=10;k++){g+=`<text x="${cx-6}" y="${cy-R*k/10+3}" text-anchor="end" font-size="9" fill="#9aa3af">${(k*0.5)%1===0?(k*0.5):(k*0.5).toFixed(1)}</text>`;}
  // capability series (purple) — plotted on all axes (0 where N/A), like the print
  g+=`<polygon points="${spokes.map((s,i)=>pt(i,s.cap!=null?s.cap:0).join(',')).join(' ')}" fill="none" stroke="#9b8cce" stroke-width="1.5"/>`;
  // maturity series (blue)
  g+=`<polygon points="${spokes.map((s,i)=>pt(i,s.mat!=null?s.mat:0).join(',')).join(' ')}" fill="rgba(37,99,235,.10)" stroke="#2563eb" stroke-width="1.8"/>`;
  spokes.forEach((s,i)=>{const m=pt(i,s.mat);g+=`<circle id="rmk-${i}" cx="${m[0]}" cy="${m[1]}" r="2" fill="#2563eb"/>`;});
  // full aspect-name labels at the rim (hoverable → highlights the axis);
  // near-vertical labels are staggered outward so dense clusters don't overlap
  spokes.forEach((s,i)=>{const a=ang(i),c=Math.cos(a);const extra=Math.abs(c)<0.32?(i%2)*16:0;
    const lx=cx+c*(R+12+extra),ly=cy+Math.sin(a)*(R+12+extra);
    const anchor=c>0.15?'start':c<-0.15?'end':'middle';
    g+=`<text x="${lx}" y="${ly+3}" text-anchor="${anchor}" font-size="10" fill="#3f4a5a" style="cursor:pointer" onmouseover="highlightSpoke(${i},true)" onmouseout="highlightSpoke(${i},false)">${s.n}. ${esc(s.name)}</text>`;});
  // domain labels bracketed at the corners (like the print)
  function cor(label,x,y,anchor,br){g+=`<path d="${br}" fill="none" stroke="${BC}" stroke-width="1.2"/><text x="${x}" y="${y}" text-anchor="${anchor}" font-size="15" font-weight="700" fill="${BC}">${label}</text>`;}
  cor('Services',26,26,'start',`M22 38 L22 16 L150 16`);
  cor('Business',W-26,26,'end',`M${W-22} 38 L${W-22} 16 L${W-150} 16`);
  cor('People',W-26,cy+70,'end',`M${W-22} ${cy+10} L${W-22} ${cy+98}`);
  cor('Technology',26,Hh-22,'start',`M22 ${Hh-40} L22 ${Hh-12} L160 ${Hh-12}`);
  cor('Process',W-26,Hh-22,'end',`M${W-22} ${Hh-40} L${W-22} ${Hh-12} L${W-180} ${Hh-12}`);
  // legend (right)
  g+=`<line x1="${W-150}" y1="${cy-30}" x2="${W-126}" y2="${cy-30}" stroke="#2563eb" stroke-width="2.2"/><text x="${W-120}" y="${cy-26}" font-size="12" fill="#3f4a5a">Maturity</text>`;
  g+=`<line x1="${W-150}" y1="${cy-10}" x2="${W-126}" y2="${cy-10}" stroke="#9b8cce" stroke-width="2.2"/><text x="${W-120}" y="${cy-6}" font-size="12" fill="#3f4a5a">Capability</text>`;
  return `<svg viewBox="0 0 ${W} ${Hh}" width="100%">${g}</svg>`;
}
// number→name legend grouped/colored by domain; hover highlights the radar axis
function socNumberLegend(domains){let gi=-1;
  return `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-top:12px">`+
   domains.map(d=>`<div style="font-size:12px"><div style="font-weight:700;color:${DOMCOL[d.key]};margin-bottom:3px;border-bottom:2px solid ${DOMCOL[d.key]};padding-bottom:2px">${esc(d.key)}</div>`+
     d.aspects.map((a,j)=>{gi++;const i=gi;return `<div class="lgi" onmouseover="highlightSpoke(${i},true)" onmouseout="highlightSpoke(${i},false)" style="color:#475569"><b style="color:${DOMCOL[d.key]}">${j+1}.</b> ${esc(a.name)}</div>`}).join('')+`</div>`).join('')+`</div>`;
}
function highlightSpoke(i,on){const ax=document.getElementById('rax-'+i);
  if(ax){ax.setAttribute('stroke',on?(ax.getAttribute('data-c')||'#0f172a'):'#dadfe6');ax.setAttribute('stroke-width',on?2.5:0.7);}
  const mk=document.getElementById('rmk-'+i);if(mk)mk.setAttribute('r',on?5:2);}
// per-domain teia (radar) of its aspects; falls back to bars when <3 aspects
function domainRadar(aspects,withCap){
  const N=aspects.length;
  if(N<3)return aspBars(aspects,withCap);
  const cx=240,cy=152,R=100,MAX=5,step=2*Math.PI/N;
  const ang=i=>-Math.PI/2+i*step,pt=(i,v)=>[cx+Math.cos(ang(i))*R*(v||0)/MAX,cy+Math.sin(ang(i))*R*(v||0)/MAX];
  let g='';
  for(let lev=1;lev<=5;lev++)g+=`<polygon points="${aspects.map((_,i)=>pt(i,lev).join(',')).join(' ')}" fill="none" stroke="#eef2f7"/>`;
  aspects.forEach((_,i)=>{const e=pt(i,5);g+=`<line x1="${cx}" y1="${cy}" x2="${e[0]}" y2="${e[1]}" stroke="#eef2f7"/>`;});
  g+=`<polygon points="${aspects.map((a,i)=>pt(i,a.matScore).join(',')).join(' ')}" fill="rgba(37,99,235,.16)" stroke="#2563eb" stroke-width="2"/>`;
  if(withCap){const cp=aspects.map((a,i)=>a.hasCapability&&a.capScore!=null?pt(i,a.capScore):null).filter(Boolean);
    if(cp.length>1)g+=`<polygon points="${cp.map(p=>p.join(',')).join(' ')}" fill="rgba(124,58,237,.10)" stroke="#7c3aed" stroke-width="1.6" stroke-dasharray="5 3"/>`;}
  // numeric values at vertices
  aspects.forEach((a,i)=>{if(a.matScore!=null){const m=pt(i,a.matScore);g+=`<circle cx="${m[0]}" cy="${m[1]}" r="2.5" fill="#2563eb"/><text x="${m[0]}" y="${m[1]-5}" text-anchor="middle" font-size="9" font-weight="700" fill="#1e3a8a" stroke="#fff" stroke-width="2.4" paint-order="stroke">${Math.round(a.matScore*10)/10}</text>`;}
    if(withCap&&a.hasCapability&&a.capScore!=null){const c=pt(i,a.capScore);g+=`<circle cx="${c[0]}" cy="${c[1]}" r="2.5" fill="#7c3aed"/><text x="${c[0]}" y="${c[1]+12}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#6d28d9" stroke="#fff" stroke-width="2.2" paint-order="stroke">${Math.round(a.capScore*10)/10}</text>`;}});
  aspects.forEach((a,i)=>{const an=ang(i),lx=cx+Math.cos(an)*(R+10),ly=cy+Math.sin(an)*(R+10);const anchor=Math.cos(an)>0.3?'start':Math.cos(an)<-0.3?'end':'middle';
    g+=`<text x="${lx}" y="${ly}" text-anchor="${anchor}" font-size="9.5" fill="#334155">${esc(a.name).slice(0,24)}</text>`;});
  return `<svg viewBox="0 0 480 300" width="100%">${g}</svg>`;
}
function radarVia(domains){
  const N=domains.length,cx=200,cy=175,R=125;
  const pt=(i,v)=>{const a=-Math.PI/2+i*2*Math.PI/N;return[cx+Math.cos(a)*R*(v||0)/100,cy+Math.sin(a)*R*(v||0)/100]};
  let g='';[25,50,75,100].forEach(L=>{g+=`<polygon points="${domains.map((_,i)=>{const a=-Math.PI/2+i*2*Math.PI/N;return[cx+Math.cos(a)*R*L/100,cy+Math.sin(a)*R*L/100].join(',')}).join(' ')}" fill="none" stroke="#e2e8f0"/>`;});
  domains.forEach((_,i)=>{const a=-Math.PI/2+i*2*Math.PI/N;g+=`<line x1="${cx}" y1="${cy}" x2="${cx+Math.cos(a)*R}" y2="${cy+Math.sin(a)*R}" stroke="#e2e8f0"/>`;});
  g+=`<polygon points="${domains.map((s,i)=>pt(i,s.tpct).join(',')).join(' ')}" fill="rgba(5,150,105,.10)" stroke="#059669" stroke-width="1.5"/>`;
  g+=`<polygon points="${domains.map((s,i)=>pt(i,s.mpct).join(',')).join(' ')}" fill="rgba(37,99,235,.30)" stroke="#2563eb" stroke-width="2"/>`;
  domains.forEach((s,i)=>{const a=-Math.PI/2+i*2*Math.PI/N;const anchor=Math.cos(a)>0.3?'start':Math.cos(a)<-0.3?'end':'middle';g+=`<text x="${cx+Math.cos(a)*(R+12)}" y="${cy+Math.sin(a)*(R+12)}" text-anchor="${anchor}" font-size="11" fill="#334155">${esc(s.key)}</text>`;});
  return `<svg viewBox="-50 0 500 350" width="100%" height="330">${g}</svg>`;
}
function aspBars(aspects,withCap){
  const H=withCap?34:26,w=600,lw=230,bw=w-lw-50;let g='';
  aspects.forEach((x,i)=>{const y=8+i*H,p=x.mpct||0,cp=x.cpct;
    g+=`<text x="0" y="${y+12}" font-size="11" fill="#334155">${esc(x.name).slice(0,32)}</text>`;
    g+=`<rect x="${lw}" y="${y+2}" width="${bw}" height="8" rx="4" fill="#eef2f7"/><rect x="${lw}" y="${y+2}" width="${bw*p/100}" height="8" rx="4" fill="${col(p)}"/>`;
    g+=`<text x="${lw+bw+6}" y="${y+10}" font-size="10" fill="#64748b">${x.mpct==null?'—':Math.round(p)+'%'}</text>`;
    if(withCap&&x.hasCapability){g+=`<rect x="${lw}" y="${y+15}" width="${bw}" height="6" rx="3" fill="#f3e8ff"/><rect x="${lw}" y="${y+15}" width="${bw*(cp||0)/100}" height="6" rx="3" fill="#7c3aed"/>`;
      g+=`<text x="${lw+bw+6}" y="${y+22}" font-size="10" fill="#7c3aed">${cp==null?'—':Math.round(cp)+'%'}</text>`;}});
  return `<svg viewBox="0 0 ${w} ${8+aspects.length*H+6}" width="100%">${g}</svg>`;
}
function lineChart(points){
  const w=620,h=200,pad=34,n=points.length;
  if(n===0)return '<p class="mini">Sem ciclos.</p>';
  const x=i=>pad+(n===1?(w-2*pad)/2:i*(w-2*pad)/(n-1)),y=v=>h-pad-(v/100)*(h-2*pad);
  let g='';[0,25,50,75,100].forEach(v=>{g+=`<line x1="${pad}" y1="${y(v)}" x2="${w-pad}" y2="${y(v)}" stroke="#eef2f7"/><text x="${pad-6}" y="${y(v)+3}" text-anchor="end" font-size="9" fill="#94a3b8">${v}</text>`;});
  const pts=points.map((p,i)=>[x(i),y(p.pct||0)]);
  g+=`<polyline points="${pts.map(p=>p.join(',')).join(' ')}" fill="none" stroke="#2563eb" stroke-width="2"/>`;
  pts.forEach((p,i)=>{g+=`<circle cx="${p[0]}" cy="${p[1]}" r="4" fill="#2563eb"/><text x="${p[0]}" y="${p[1]-9}" text-anchor="middle" font-size="10" font-weight="700" fill="#2563eb">${points[i].pct==null?'—':Math.round(points[i].pct)+'%'}</text><text x="${p[0]}" y="${h-pad+14}" text-anchor="middle" font-size="10" fill="#64748b">${esc(points[i].label)}</text>`;});
  return `<svg viewBox="0 0 ${w} ${h}" width="100%">${g}</svg>`;
}

// ===== modal/helpers =====
function modal(h){document.getElementById('modal-root').innerHTML=`<div class="overlay" onclick="if(event.target===this)closeModal()"><div class="modal">${h}</div></div>`;}
function closeModal(){document.getElementById('modal-root').innerHTML='';}
function esc(s){return (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function go(v,o={}){Object.assign(state,o);state.view=v;render()}
function orgById(id){return db.orgs.find(o=>o.id===id)}
function asmById(id){return db.assessments.find(a=>a.id===id)}
function asmsFor(orgId,slug){return db.assessments.filter(a=>a.orgId===orgId&&(!slug||a.frameworkSlug===slug))}
function findQ(slug,code){const fw=FW[slug];let R=null;fw.domains.forEach(d=>d.aspects.forEach(a=>a.questions.forEach(q=>{if(q.code===code)R={q,a,d}})));return R}
function helpModal(slug,code){const r=findQ(slug,code);if(!r)return;const A=ans(state.assessmentId)[code]||{};
  const levels=r.q.levels.map(l=>`<div class="lvl ${A.cur===l.v?'sel':''}"><b>${l.v}</b><span><b>${esc(l.label)}</b>${l.desc?' — '+esc(l.desc):''}</span></div>`).join('');
  modal(`<div class="mh"><b>${esc(r.q.code)}</b><span class="badge ${r.q.type==='C'?'p':'b'}">${r.q.type==='C'?'Capability':'Maturity'}</span>
     <span class="mini">${esc(r.d.key)} · ${esc(r.a.name)}</span><button class="btn ghost sm" style="margin-left:auto" onclick="closeModal()">Fechar</button></div>
    <div class="mb"><p style="font-size:15px;margin:0 0 4px">${esc(r.q.text)}</p>
      ${r.q.remark?`<div class="card" style="background:#f8fafc;margin:10px 0"><div class="pad" style="padding:12px"><div class="mini" style="font-weight:700;margin-bottom:4px">O que avaliar / o que fazer</div>${esc(r.q.remark)}</div></div>`:''}
      <div class="mini" style="font-weight:700;margin:12px 0 6px">O que cada nível significa</div>${levels}
      <p class="mini" style="margin-top:12px">Selecione no formulário o nível que melhor descreve a situação atual.</p></div>`);
}

// ===== auth =====
function viewLogin(){return `<div style="max-width:380px;margin:8vh auto"><div class="card"><div class="pad">
  <div style="text-align:center;margin-bottom:12px"><div class="logo" style="justify-content:center"><span class="dot"></span>Viaconnect SOC</div><div class="mini">Acesso interno · Health Check de SOC</div></div>
  <label class="f">Usuário</label><input id="lu" autofocus/><div style="height:10px"></div><label class="f">Senha</label><input id="lp" type="password"/>
  <div id="lerr" class="mini" style="color:var(--red);height:16px;margin-top:6px"></div>
  <button class="btn" style="width:100%" onclick="doLogin()">Entrar</button>
  <div class="mini" style="text-align:center;margin-top:10px">padrão: admin / admin</div></div></div></div>`;}
function doLogin(){const u=document.getElementById('lu').value.trim(),p=document.getElementById('lp').value;
  const user=db.users.find(x=>x.username===u&&x.password===p);if(!user){document.getElementById('lerr').textContent="Usuário ou senha inválidos";return}
  db.session=user.username;save();go('orgs');}
function logout(){db.session=null;save();go('login')}

// ===== organizations =====
function viewOrgs(){
  const rows=db.orgs.map(o=>`<tr><td><b>${esc(o.name)}</b></td><td>${esc(o.sector||'—')}</td><td>${asmsFor(o.id).length}</td>
    <td style="text-align:right"><button class="btn sm" onclick="go('org',{orgId:${o.id},orgTab:'assessment'})">Abrir</button></td></tr>`).join('');
  return `<h1>Organizações</h1><p class="sub">Cadastre organizações e conduza avaliações por ciclos.</p>
    <div class="card"><h3>Nova organização</h3><div class="pad"><div class="row">
      <div style="flex:1;min-width:200px"><label class="f">Nome *</label><input id="on"/></div>
      <div style="flex:1;min-width:160px"><label class="f">Setor</label><input id="os"/></div>
      <button class="btn" onclick="createOrg()">Criar</button></div></div></div>
    <div class="card"><div class="pad">${db.orgs.length?`<table><tr><th>Organização</th><th>Setor</th><th>Avaliações</th><th></th></tr>${rows}</table>`:'<div class="empty">Nenhuma organização ainda.</div>'}</div></div>`;}
function createOrg(){const n=document.getElementById('on').value.trim();if(!n)return;db.orgs.push({id:nid(),name:n,sector:document.getElementById('os').value.trim()});save();render();}

// ===== Viaconnect knowledge base: gaps por domínio + ações/entregáveis reais (Sophos XDR; Standard/Advanced) =====
const KB={
 'CTI':{fw:'CTI-CMM',gap:'Inteligência ad hoc, sem requisitos prioritários (PIRs) nem produtos estruturados; pouca correlação de IoCs com o ambiente.',
   actions:[
     {t:'Integração de feeds de CTI e enriquecimento automático de alertas',d:'Feeds Sophos + Marketplace, correlação de IoCs no Sophos XDR.',tier:'Standard'},
     {t:'Relatório de CTI — credenciais vazadas (OSINT/dark web)',d:'Monitoramento trimestral com alertas para contas privilegiadas.',tier:'Advanced'},
     {t:'Definir PIRs e produtos tático/operacional/estratégico',d:'Requisitos prioritários de inteligência alinhados ao negócio.',tier:'Processo'}]},
 'Threat Hunting':{fw:'PEAK / HMM',gap:'Operação reativa, dependente de alertas; sem caça proativa por hipóteses nem medição de cobertura.',
   actions:[
     {t:'Threat Hunting dedicado — campanhas semanais (TaHiTI/PEAK)',d:'Hunts intel-, hypothesis- e analytics-driven com analista dedicado (L3).',tier:'Advanced'},
     {t:'Cobertura MITRE ATT&CK medida continuamente',d:'Mapeamento de TTPs, gaps de detecção e novos casos de uso.',tier:'Advanced'}]},
 'Detection Eng':{fw:'Detection Engineering Maturity Matrix',gap:'Detecções padrão sem versionamento, testes ou mapeamento a TTPs; pouca otimização.',
   actions:[
     {t:'Biblioteca de regras de detecção padrão (Sophos XDR)',d:'Detecção mantida pela Viaconnect, ajuste de thresholds e redução de FP.',tier:'Standard'},
     {t:'Engenharia de detecção customizada (detection-as-code)',d:'Regras versionadas, testadas e mapeadas ao ATT&CK, otimizadas por findings de hunting.',tier:'Advanced'}]},
 'DFIR':{fw:'CREST CSIR',gap:'Resposta improvisada, sem ciclo formal nem playbooks por ativo crítico; lições não retroalimentam.',
   actions:[
     {t:'Resposta a incidentes completa — ciclo SANS PICERL + RCA',d:'Detecção→contenção→erradicação→recuperação, post-mortem e métricas (MTTD/MTTR).',tier:'Standard'},
     {t:'Playbooks de ativos críticos + Líder de IR dedicado + Sala de Crise',d:'Pool 100h/400h, matriz RACI e linha do tempo auditável.',tier:'Advanced'}]},
 'CSIRT':{fw:'SIM3 (O/H/T/P)',gap:'Mandato, processos e governança pouco formalizados; escalonamento e RACI implícitos.',
   actions:[
     {t:'Estrutura L1/L2 24/7, CIRP documentado e matriz RACI',d:'Triagem e escalonamento formais, handover entre turnos.',tier:'Standard'},
     {t:'Governança executiva: TAM dedicado, QBR trimestral, comunicação a reguladores',d:'Interface estratégica, templates ANPD/BACEN, roadmap de maturidade.',tier:'Advanced'}]},
 'PSIRT':{fw:'FIRST PSIRT Services Framework',gap:'Sem processo formal de recebimento/triagem e divulgação coordenada de vulnerabilidades de produto.',
   actions:[
     {t:'Acompanhamento de CVEs críticos com impacto ao parque',d:'Correlação com exposição externa e priorização de remediação.',tier:'Advanced'},
     {t:'Processo de recebimento, triagem e divulgação coordenada (CVD)',d:'Ponto de entrada, qualificação e advisories padronizados.',tier:'Processo'}]},
 'Deception':{fw:'MITRE Engage',gap:'Sem uso de deception; oportunidade de detecção de alta fidelidade ainda não explorada.',
   actions:[
     {t:'Implantar honeytokens/decoys integrados ao Sophos XDR (MITRE Engage)',d:'Iscas de alta fidelidade para expor movimento lateral; alertas priorizados ao SOC.',tier:'Futuro'}]},
 'Vuln Mgmt':{fw:'SANS VMMM (PIACT)',gap:'Identificação pontual e sem priorização por exposição/exploração ativa; tratamento não medido.',
   actions:[
     {t:'Health Check Sophos (EDR + Firewall) com gap analysis',d:'Assessment de configuração, score de maturidade e plano de ação priorizado.',tier:'Standard'},
     {t:'Relatório de Exposição Externa (EASM) — CVSS e priorização',d:'Mapeamento trimestral da superfície externa e acompanhamento de CVEs.',tier:'Advanced'}]},
 'Automacao':{fw:'SOC-CMM (Automation & Orchestration)',gap:'Automação pontual, sem padronização nem medição de ganho; processos não orquestrados.',
   actions:[
     {t:'Automação de triagem/enriquecimento e resposta (playbooks Sophos XDR)',d:'Isolamento, bloqueio de IoC e quarentena automatizados; redução de MTTR.',tier:'Standard'},
     {t:'Orquestração ampliada (SOAR) com playbooks versionados e medição',d:'Casos priorizados por ganho/esforço, erro tratado e ganho medido.',tier:'Advanced'}]}
};
const KB_DEFAULT={fw:'SOC-CMM',gap:'Capacidade pouco estruturada para o nível desejado.',actions:[{t:'Estruturar o domínio com base no framework de referência',d:'Definir processo, responsáveis e métricas.',tier:'Processo'}]};
function kb(key){return KB[key]||KB_DEFAULT;}
function defaultPriority(s){return s==null?'media':(s<2?'alta':s<3.5?'media':'baixa');}
function horizonOf(s,pri){let b=s==null?6:(s<2?3:s<3.5?6:12);if(pri==='alta')b=Math.min(b,3);else if(pri==='baixa')b=Math.max(b,12);else if(pri==='media'&&b===12)b=6;return b;}
function actionHorizon(domH,tier){const steps=[3,6,12];let i=steps.indexOf(domH);if(tier==='Advanced'||tier==='Futuro')i=Math.min(2,i+1);return steps[i];}
// latest assessed "Domínios" cycle for the org
function dominiosLatest(orgId){const fw=FW['viaconnect-soc'];
  return asmsFor(orgId,'viaconnect-soc').filter(a=>dashboard(fw,ans(a.id)).answered>0).sort((a,b)=>(b.date||'').localeCompare(a.date||''))[0]||null;}
function domViews(a){const fw=FW['viaconnect-soc'],dd=dashboard(fw,ans(a.id));
  return dd.domains.map(d=>({key:d.key,full:d.name,fw:(kb(d.key).fw),score:d.mpct==null?null:d.mpct/100*5,answered:d.answered,total:d.total,assessed:d.answered>0}));}
function orgRm(o){o.rm=o.rm||{excl:{},pri:{}};o.rm.sel=o.rm.sel||{};return o.rm;}
function rmToggle(id,key){const o=orgById(id),rm=orgRm(o);rm.excl[key]=!rm.excl[key];save();render();}
function recIncluded(rm,key,i){return rm.sel[key+'|'+i]!==false;}
function recSel(id,key,i){const o=orgById(id),rm=orgRm(o);const k=key+'|'+i;rm.sel[k]=(rm.sel[k]===false);save();render();}
// Entregáveis Viaconnect (matriz Standard/Advanced dos documentos)
const DELIV=[
 {n:'Monitoramento e resposta a ameaças 24/7',std:'✓',adv:'✓'},
 {n:'Relatórios mensais (KPIs/KRIs)',std:'✓',adv:'✓'},
 {n:'Health Check Sophos (EDR e Firewall)',std:'✓',adv:'✓'},
 {n:'Automação (playbooks Sophos XDR)',std:'✓',adv:'✓'},
 {n:'Análise de Causa Raiz (RCA)',std:'✓',adv:'✓'},
 {n:'Resposta completa a incidentes (SANS PICERL)',std:'✓',adv:'✓'},
 {n:'Integrações para enriquecimento (Marketplace Sophos)',std:'✓',adv:'✓'},
 {n:'Suporte direto durante incidentes',std:'✓',adv:'✓'},
 {n:'Threat Hunting dedicado (campanhas semanais)',std:'',adv:'✓'},
 {n:'Engenharia de detecção customizada',std:'',adv:'✓'},
 {n:'Sala de Crise',std:'sob demanda',adv:'pool 100h/400h'},
 {n:'Dashboards customizados',std:'',adv:'✓'},
 {n:'Playbooks de ativos críticos',std:'',adv:'✓'},
 {n:'Líder dedicado de resposta a incidentes',std:'',adv:'✓'},
 {n:'TAM dedicado (consiglieri) + QBR',std:'',adv:'✓'},
 {n:'Assessment de maturidade operacional',std:'',adv:'✓'},
 {n:'Relatório de CTI — credenciais vazadas',std:'',adv:'✓ (trimestral)'},
 {n:'Relatório de Exposição Externa (EASM)',std:'',adv:'✓ (trimestral)'}
];
function orgTier(o){return o.tier||'standard';}
function setTier(id,t){orgById(id).tier=t;save();render();}
function setDeliv(id,n,v){const o=orgById(id);o.deliv=o.deliv||{};o.deliv[n]=v;save();state._noscroll=true;render();}
function rmPri(id,key,v){const o=orgById(id),rm=orgRm(o);rm.pri[key]=v;save();render();}
function setOrgTab(t){state.orgTab=t;render();}

// ===== Claude (IA) integration: a framework-fed "skill" turns the Domínios assessment into recommendations =====
const REC_SCHEMA={type:'object',additionalProperties:false,required:['resumo','dominios'],properties:{
  resumo:{type:'string'},
  dominios:{type:'array',items:{type:'object',additionalProperties:false,required:['dominio','diagnostico','acoes'],properties:{
    dominio:{type:'string'},diagnostico:{type:'string'},
    acoes:{type:'array',items:{type:'object',additionalProperties:false,required:['titulo','descricao','horizonte','entregavel'],properties:{
      titulo:{type:'string'},descricao:{type:'string'},
      horizonte:{type:'string',enum:['0-3 meses','3-6 meses','6-12 meses']},
      entregavel:{type:'string'}
    }}}}}}}};
// the "skill": a reusable system prompt fed with the frameworks + Viaconnect deliverables (kept in sync with KB/DELIV)
function claudeSkill(){
  const doms=Object.keys(KB).map(k=>{const v=KB[k];
    const acts=v.actions.map(a=>`      - [${a.tier}] ${a.t}: ${a.d}`).join('\n');
    return `• ${k} — framework de referência: ${v.fw}\n    Lacuna típica: ${v.gap}\n    Entregáveis Viaconnect aplicáveis:\n${acts}`;}).join('\n');
  const deliv=DELIV.map(d=>`  - ${d.n} | Standard: ${d.std||'não incluso'} | Advanced: ${d.adv||'não incluso'}`).join('\n');
  const escala=LEVELNAME.map((n,i)=>`${i} = ${n}`).join('  |  ');
  return [
    'Você é um consultor sênior de maturidade de SOC da Viaconnect. Seu trabalho é transformar o resultado do assessment de Domínios (Health Check) em recomendações precisas, acionáveis e fundamentadas nos frameworks e nos entregáveis reais da Viaconnect.',
    '',
    'ESCALA DE MATURIDADE (0 a 5): '+escala+'.',
    '',
    'STACK TECNOLÓGICO VIACONNECT: Sophos XDR, Sophos Central e Sophos Firewall (com integrações do Marketplace Sophos). Frameworks transversais: NIST CSF, NIST SP 800-61, MITRE ATT&CK, SANS PICERL e TaHiTI/PEAK.',
    '',
    'DOMÍNIOS, FRAMEWORKS DE REFERÊNCIA, LACUNAS TÍPICAS E ENTREGÁVEIS:',
    doms,
    '',
    'MATRIZ DE ENTREGÁVEIS (disponibilidade por plano contratado):',
    deliv,
    '',
    'DIRETRIZES PARA AS RECOMENDAÇÕES:',
    '1. Baseie-se EXCLUSIVAMENTE no resultado do assessment informado pelo usuário e nos frameworks/entregáveis acima.',
    '2. Para cada domínio em escopo, escreva um diagnóstico específico: o que o nível atual indica e o que falta para alcançar o próximo nível. Evite generalidades.',
    '3. Cada ação deve citar um entregável Viaconnect concreto (campo "entregavel") e ser viável com o stack Sophos.',
    '4. Defina o horizonte por prioridade: fundação (Standard) e domínios de baixa maturidade em "0-3 meses"; consolidação em "3-6 meses"; evolução proativa/Advanced em "6-12 meses".',
    '5. Priorize os domínios de menor maturidade. Seja conciso e executivo, porém concreto. Responda inteiramente em português do Brasil.'
  ].join('\n');
}
function buildRecPrompt(o,a){
  const rm=orgRm(o);
  const dd=dashboard(FW['viaconnect-soc'],ans(a.id));
  const overall=dd.overall==null?null:dd.overall/100*5;
  const views=domViews(a).filter(v=>v.assessed);
  const inScope=views.filter(v=>!rm.excl[v.key]);
  const excl=views.filter(v=>rm.excl[v.key]).map(v=>v.key);
  const tier=orgTier(o)==='advanced'?'SOC Advanced':'SOC Standard';
  const lines=inScope.map(v=>`- ${v.key} (${v.fw}): ${fmt1(v.score)}/5 — ${levelName(v.score)}`).join('\n');
  return [
    'Organização: '+o.name+(o.sector?' ('+o.sector+')':''),
    'Plano contratado: '+tier,
    'Ciclo avaliado: '+(a.cycle||'')+(a.date?' ('+a.date+')':''),
    'Postura geral: '+fmt1(overall)+'/5 — '+levelName(overall)+'.',
    '',
    'Resultado por domínio (escala 0–5):',
    lines,
    (excl.length?'\nDomínios fora de escopo (NÃO recomende para eles): '+excl.join(', '):''),
    '',
    'Gere: (1) um resumo executivo da postura e das prioridades; (2) para cada domínio em escopo, um diagnóstico preciso e ações concretas com entregável Viaconnect e horizonte.'
  ].join('\n');
}
function horizonChip(h){const m={'0-3 meses':['#e0f2fe','#075985'],'3-6 meses':['#fef3c7','#854d0e'],'6-12 meses':['#ede9fe','#6d28d9']};const c=m[h]||['#f1f5f9','#475569'];return `<span class="hchip" style="background:${c[0]};color:${c[1]}">${esc(h)}</span>`;}
function aiBlock(o,a){
  if(o.aiBusy)return `<div class="card"><div class="pad" style="display:flex;align-items:center;gap:12px"><span class="spin"></span><div><b>Gerando recomendações com Claude…</b><div class="mini">Analisando o resultado do assessment de Domínios à luz dos frameworks.</div></div></div></div>`;
  const r=(o.aiRecs||{})[a.id];if(!r)return '';
  const doms=(r.dominios||[]).map(d=>`<div class="scard" style="margin-bottom:10px"><div style="font-size:14px;font-weight:700;margin-bottom:5px">${esc(d.dominio)}</div>
      <div class="mini" style="margin-bottom:8px;line-height:1.5">${esc(d.diagnostico)}</div>
      ${(d.acoes||[]).map(ac=>`<div class="act"><div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">${horizonChip(ac.horizonte)}<span class="hchip" style="background:#eef2f7;color:#475569">${esc(ac.entregavel)}</span></div>
        <div style="font-size:13px;font-weight:600;margin-top:5px">${esc(ac.titulo)}</div><div class="mini" style="margin-top:2px">${esc(ac.descricao)}</div></div>`).join('')}</div>`).join('');
  return `<div class="card"><h3>✨ Recomendações geradas por IA <span class="badge p">Claude</span><span class="mini" style="font-weight:400;margin-left:auto">${esc(r.model||'')} · ${new Date(r.ts).toLocaleString('pt-BR')}</span></h3>
    <div class="pad"><p style="font-size:14px;line-height:1.6;margin:0 0 14px">${esc(r.resumo)}</p>${doms}</div></div>`;
}
async function generateRecs(orgId){
  const o=orgById(orgId);const cfg=db.claude||{};
  if(!cfg.apiKey){alert('Configure a chave da API do Claude em Configurações para gerar recomendações.');return go('config');}
  const a=dominiosLatest(orgId);if(!a)return;
  o.aiBusy=true;o.aiErr=null;save();state._noscroll=true;render();
  try{
    const body={model:cfg.model||'claude-opus-4-8',max_tokens:8000,
      system:claudeSkill()+(cfg.extra?'\n\nINSTRUÇÕES ADICIONAIS DO ANALISTA:\n'+cfg.extra:''),
      messages:[{role:'user',content:buildRecPrompt(o,a)}],
      output_config:{format:{type:'json_schema',schema:REC_SCHEMA}}};
    const res=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',
      headers:{'content-type':'application/json','x-api-key':cfg.apiKey,'anthropic-version':'2023-06-01','anthropic-dangerous-direct-browser-access':'true'},
      body:JSON.stringify(body)});
    const data=await res.json();
    if(!res.ok)throw new Error((data&&data.error&&data.error.message)||('HTTP '+res.status));
    if(data.stop_reason==='refusal')throw new Error('A solicitação foi recusada pelo modelo.');
    const txt=(data.content||[]).filter(b=>b.type==='text').map(b=>b.text).join('');
    const parsed=JSON.parse(txt);
    o.aiRecs=o.aiRecs||{};o.aiRecs[a.id]=Object.assign({},parsed,{model:body.model,ts:new Date().toISOString()});
  }catch(e){o.aiErr=String((e&&e.message)||e);}
  o.aiBusy=false;save();state._noscroll=true;render();
}

function viewOrg(){
  const o=orgById(state.orgId);if(!o)return go('orgs');
  const tab=state.orgTab||'assessment';
  const tabs=[['assessment','Assessment'],['evolucao','Evolução de postura'],['recomendacoes','Recomendações'],['roadmap','Roadmap'],['entregaveis','Entregáveis Viaconnect']];
  const bar=`<div class="tabbar no-print">${tabs.map(([k,l])=>`<button class="${tab===k?'on':''}" onclick="setOrgTab('${k}')">${l}</button>`).join('')}</div>`;
  const body=({assessment:orgAssessment,evolucao:orgEvolucao,recomendacoes:orgRecs,roadmap:orgRoadmap,entregaveis:orgEntregaveis}[tab]||orgAssessment)(o);
  return `<a onclick="go('orgs')">← Organizações</a><h1 style="margin-top:8px">${esc(o.name)}</h1>
    <p class="sub">${esc(o.sector||'')} · jornada de maturidade do SOC</p>${bar}${body}`;
}

function orgAssessment(o){
  let blocks='';
  FRAMEWORKS.forEach(fw=>{const list=asmsFor(o.id,fw.slug).sort((a,b)=>(a.date||'').localeCompare(b.date||''));
    const rows=list.map(a=>{const dd=dashboard(fw,ans(a.id));
      return `<tr><td><b>${esc(a.cycle)}</b></td><td>${esc(a.date||'—')}</td>
        <td><span class="badge ${a.status==='completed'?'g':'a'}">${a.status==='completed'?'Concluída':'Em andamento'}</span></td>
        <td>${dd.overall==null?'—':Math.round(dd.overall)+'%'}</td><td class="mini">${dd.answered}/${dd.total}</td><td class="mini">${esc(a.filledBy||'—')}</td>
        <td style="text-align:right;white-space:nowrap"><button class="btn ghost sm" onclick="go('run',{assessmentId:${a.id},dIdx:0,aIdx:0})">Preencher</button>
          <button class="btn ghost sm" onclick="go('dashboard',{assessmentId:${a.id}})">Dashboard</button><button class="btn ghost sm" onclick="exportXlsx(${a.id})" title="Exportar assessment em XLSX">⤓ XLSX</button><button class="btn danger sm" onclick="delAsm(${a.id})">×</button></td></tr>`;}).join('');
    const naAsp=fw.domains.reduce((s,d)=>s+d.aspects.length,0);
    blocks+=`<div class="card"><h3>${esc(fw.name)} <span class="badge b">${fw.domains.length} domínios · ${naAsp} aspectos</span>
        <button class="btn sm" style="margin-left:auto" onclick="newCycle(${o.id},'${fw.slug}')">+ Novo ciclo</button></h3>
      <div class="pad">${list.length?`<table><tr><th>Ciclo</th><th>Data</th><th>Status</th><th>Geral</th><th>Cobertura</th><th>Preenchido por</th><th></th></tr>${rows}</table>`:'<div class="mini">Nenhum ciclo ainda.</div>'}</div></div>`;});
  return `<div class="row no-print" style="align-items:center;margin:-6px 0 14px;gap:10px">
      <p class="mini" style="margin:0;flex:1;min-width:220px">Os três tipos de avaliação. Crie ciclos para acompanhar a evolução. Exporte cada ciclo (botão <b>⤓ XLSX</b>) ou importe um arquivo exportado — organização · domínio · nota · meta.</p>
      <input type="file" id="impxlsx" accept=".xlsx,.xls" style="display:none" onchange="if(this.files&&this.files[0]){importXlsx(${o.id},this.files[0]);this.value='';}"/>
      <button class="btn ghost sm" onclick="document.getElementById('impxlsx').click()" title="Importar um assessment em XLSX (cria um ciclo)">⤴ Importar XLSX</button>
    </div>${blocks}`;}

// ---- Evolução de postura (assessment de Domínios por ciclos) ----
function orgEvolucao(o){
  const fw=FW['viaconnect-soc'];
  const cycles=asmsFor(o.id,'viaconnect-soc').filter(a=>dashboard(fw,ans(a.id)).answered>0).sort((a,b)=>(a.date||'').localeCompare(b.date||''));
  if(!cycles.length)return `<div class="card"><div class="empty">Crie e preencha ciclos da avaliação <b>Domínios</b> para acompanhar a evolução de postura.</div></div>`;
  const evo=cycles.map(c=>{const d=dashboard(fw,ans(c.id));return {label:(c.cycle.split('—')[0].trim()||c.cycle).slice(0,14),score:d.overall==null?null:d.overall/100*5,c:c};});
  const first=dashboard(fw,ans(cycles[0].id)),last=dashboard(fw,ans(cycles[cycles.length-1].id));
  const f05=first.overall==null?null:first.overall/100*5,l05=last.overall==null?null:last.overall/100*5;
  const delta=(f05!=null&&l05!=null)?l05-f05:null;
  // per-domain delta first→last
  const fmap={};first.domains.forEach(d=>fmap[d.key]=d.mpct==null?null:d.mpct/100*5);
  const rows=last.domains.map(d=>{const cur=d.mpct==null?null:d.mpct/100*5,prev=fmap[d.key];const dl=(cur!=null&&prev!=null)?cur-prev:null;
    return `<tr><td><b>${esc(d.key)}</b></td><td>${prev==null?'—':fmt1(prev)}</td><td>${cur==null?'—':fmt1(cur)}</td>
      <td>${dl==null?'—':`<span class="lvlpill" style="background:${dl>0?'#dcfce7':dl<0?'#fee2e2':'#f1f5f9'};color:${dl>0?'#166534':dl<0?'#991b1b':'#475569'}">${dl>0?'+':''}${fmt1(dl)}</span>`}</td></tr>`;}).join('');
  return `<div class="card"><h3>Evolução da maturidade geral — Domínios <span class="mini" style="font-weight:400">· ${cycles.length} ciclo(s)</span>
      ${delta!=null?`<span style="margin-left:auto" class="lvlpill" style="background:${delta>=0?'#dcfce7':'#fee2e2'};color:${delta>=0?'#166534':'#991b1b'}">${delta>=0?'+':''}${fmt1(delta)} desde o 1º ciclo</span>`:''}</h3>
    <div class="pad">${ec('ec-orgevo',230,ecEvolution(evo))}</div></div>
   <div class="card"><h3>Evolução por domínio (1º → último ciclo)</h3><div class="pad"><table>
     <tr><th>Domínio</th><th>Inicial</th><th>Atual</th><th>Δ</th></tr>${rows}</table></div></div>`;
}

// ---- Recomendações (gaps × frameworks dos domínios; geração com IA opcional) ----
function orgRecs(o){
  const a=dominiosLatest(o.id);
  if(!a)return `<div class="card"><div class="empty">Preencha um ciclo de <b>Domínios</b> para gerar recomendações com base na postura atual.</div></div>`;
  const rm=orgRm(o);
  const views=domViews(a).filter(v=>v.assessed&&!rm.excl[v.key]);
  const dd=dashboard(FW['viaconnect-soc'],ans(a.id));
  const overall=dd.overall==null?null:dd.overall/100*5;
  const sorted=views.slice().sort((x,y)=>(x.score||0)-(y.score||0));
  const worst=sorted.slice(0,3);
  const worstTxt=worst.map(v=>`<b>${esc(v.key)}</b> (${fmt1(v.score)})`).join(', ');
  const tierLabel=orgTier(o)==='advanced'?'SOC Advanced':'SOC Standard';
  const cfgOk=!!(db.claude&&db.claude.apiKey);
  const intro=`A postura geral atual da <b>${esc(o.name)}</b> está em <b>${fmt1(overall)}/5</b> — nível <b>${levelName(overall)}</b> —, considerando ${views.length} domínio(s) em escopo no plano <b>${tierLabel}</b>. `
    +(worst.length?`As lacunas mais críticas estão em ${worstTxt}, que devem concentrar os primeiros ciclos de evolução. `:'')
    +`Cada domínio abaixo é comparado ao seu framework de referência, e as ações apontam o entregável Viaconnect (Sophos XDR/Central/Firewall) que fecha o gap.`;
  const header=`<div class="card"><h3>Resumo executivo de recomendações</h3><div class="pad">
     <p style="font-size:14px;line-height:1.6;margin:0 0 12px">${intro}</p>
     <div class="row" style="align-items:center;gap:10px">
       <button class="btn" ${o.aiBusy?'disabled':''} onclick="generateRecs(${o.id})">${o.aiBusy?'Gerando…':'✨ Gerar com Claude'}</button>
       <span class="mini" style="flex:1;min-width:200px">Gera uma análise sob medida com IA a partir do resultado do assessment de Domínios e dos frameworks de referência.</span></div>
     ${!cfgOk?`<div class="mini" style="margin-top:8px;color:var(--amber)">⚠ Configure a chave da API do Claude em <a onclick="go('config')">Configurações</a> para habilitar a geração.</div>`:''}
     ${o.aiErr?`<div class="mini" style="margin-top:8px;color:var(--red)">Falha ao gerar: ${esc(o.aiErr)}</div>`:''}
     <p class="mini" style="margin:10px 0 0">Abaixo, a análise por domínio fundamentada nos frameworks (NIST CSF, NIST SP 800-61, MITRE ATT&CK, SANS PICERL, TaHiTI/PEAK). <b>Inclua/remova</b> recomendações para montar o <b>Roadmap</b>.</p></div></div>`;
  const ai=aiBlock(o,a);
  const cards=sorted.map(v=>{const k=kb(v.key);
    const acts=k.actions.map((act,i)=>{const on=recIncluded(rm,v.key,i);
      return `<div class="act" style="display:flex;gap:10px;align-items:flex-start;${on?'':'opacity:.55'}">
        <div style="flex:1"><div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span style="font-size:13px;font-weight:600">${esc(act.t)}</span><span class="tierp ${act.tier}">${act.tier}</span></div>
          <div class="mini" style="margin-top:3px">${esc(act.d)}</div></div>
        <button class="chip${on?' on':''}" onclick="recSel(${o.id},'${esc(v.key)}',${i})">${on?'✓ No roadmap':'+ Incluir'}</button></div>`;}).join('');
    return `<div class="scard" style="margin-bottom:12px"><div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <b>${esc(v.key)}</b><span class="mini">${esc(v.fw)}</span>
        <span style="margin-left:auto" class="lvlpill" style="background:${bandSoft(v.score)};color:${bandText(v.score)}">${fmt1(v.score)} · ${levelName(v.score)}</span></div>
      <div class="mini" style="margin:8px 0"><b>Lacuna:</b> ${esc(k.gap)}</div>
      <div class="mini" style="font-weight:700;margin-bottom:6px">Recomendações <span style="font-weight:400">— inclua/remova do roadmap</span></div>${acts}</div>`;}).join('');
  return header+ai
    +`<h2>Análise por domínio <span class="mini">(do menor ao maior nível · alimenta o Roadmap)</span></h2>${cards||'<div class="card"><div class="empty">Nenhum domínio em escopo. Reative domínios na aba Roadmap.</div></div>'}`;
}

// ---- Roadmap (ações priorizáveis por horizonte 3/6/12 meses) ----
function orgRoadmap(o){
  const a=dominiosLatest(o.id);
  if(!a)return `<div class="card"><div class="empty">Preencha um ciclo de <b>Domínios</b> para gerar o roadmap.</div></div>`;
  const rm=orgRm(o);
  const allViews=domViews(a).filter(v=>v.assessed);
  // priorização — segmented control (sem combo box), linhas alinhadas
  const PRI=[['alta','Alta'],['media','Média'],['baixa','Baixa']];
  const cfg=allViews.map(v=>{const inc=!rm.excl[v.key];const pri=rm.pri[v.key]||defaultPriority(v.score);
    const seg=`<div class="segp">${PRI.map(([p,l])=>`<button class="${pri===p?'on '+p:''}" ${inc?'':'disabled'} onclick="rmPri(${o.id},'${esc(v.key)}','${p}')">${l}</button>`).join('')}</div>`;
    return `<div class="prirow"><label style="display:flex;gap:9px;align-items:center;cursor:pointer;flex:1;min-width:200px"><input type="checkbox" ${inc?'checked':''} onchange="rmToggle(${o.id},'${esc(v.key)}')"/> <b>${esc(v.key)}</b> <span class="mini" style="font-weight:400">${esc(v.fw)}</span></label>
      <span class="lvlpill" style="background:${bandSoft(v.score)};color:${bandText(v.score)};flex:0 0 auto">${fmt1(v.score)} · ${levelName(v.score)}</span>${seg}</div>`;}).join('');
  // build actions per horizon
  const cols={3:[],6:[],12:[]};
  allViews.filter(v=>!rm.excl[v.key]).forEach(v=>{const pri=rm.pri[v.key]||defaultPriority(v.score);const dh=horizonOf(v.score,pri);
    kb(v.key).actions.forEach((act,i)=>{if(!recIncluded(rm,v.key,i))return;const h=actionHorizon(dh,act.tier);
      cols[h].push({dom:v.key,score:v.score,pri,...act});});});
  // sort each column by score asc (worst first)
  Object.keys(cols).forEach(h=>cols[h].sort((x,y)=>(x.score||0)-(y.score||0)));
  const total=cols[3].length+cols[6].length+cols[12].length;
  const HZ={3:['Curto prazo','3 meses','#2563eb'],6:['Médio prazo','6 meses','#d97706'],12:['Longo prazo','12 meses','#7c3aed']};
  const colHtml=[3,6,12].map(h=>{const t=HZ[h][0],sub=HZ[h][1],c=HZ[h][2];
    return `<div class="hz" style="border-top:3px solid ${c}">
      <div class="hzh"><span class="hdot" style="background:${c}"></span><div><div style="font-size:13px;font-weight:700">${t}</div><div class="mini">${sub} · ${cols[h].length} ação(ões)</div></div></div>
      ${cols[h].length?cols[h].map(x=>`<div class="act"><div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap"><span class="badge" style="font-size:10px">${esc(x.dom)}</span><span class="tierp ${x.tier}">${x.tier}</span></div>
        <div style="font-size:13px;font-weight:600;margin-top:5px">${esc(x.t)}</div><div class="mini" style="margin-top:2px">${esc(x.d)}</div></div>`).join(''):'<div class="mini" style="padding:6px 0">Sem ações neste horizonte.</div>'}</div>`;}).join('');
  return `<div class="card"><h3>Priorização <span class="mini" style="font-weight:400">· inclua domínios e defina a prioridade</span></h3>
     <div class="pad"><p class="mini" style="margin:0 0 4px">Desmarque um domínio para tirá-lo da análise; ajuste a prioridade para reordenar os horizontes. As ações vêm das selecionadas na aba <b>Recomendações</b>.</p>${cfg||'<div class="mini">Nenhum domínio avaliado.</div>'}</div></div>
   <div class="card"><h3>Roadmap de ações — SOC Viaconnect <span class="badge b" style="margin-left:auto">${total} ações</span></h3>
     <div class="pad"><p class="mini" style="margin:0 0 12px">Recomendações técnicas considerando o stack (Sophos XDR/Central/Firewall) e os entregáveis Viaconnect. A fundação (Standard) vem primeiro; a evolução proativa (Advanced) na sequência.</p>
     <div class="dgrid3">${colHtml}</div></div></div>`;
}

// ---- Entregáveis Viaconnect (notas 1–5 conforme o tier contratado) ----
function orgEntregaveis(o){
  const tier=orgTier(o);o.deliv=o.deliv||{};
  const items=DELIV.filter(x=>tier==='advanced'?(x.adv):(x.std));
  const scored=items.map(x=>o.deliv[x.n]).filter(v=>v!=null);
  const avg=scored.length?scored.reduce((a,b)=>a+b,0)/scored.length:null;
  const seg=(n,val)=>`<div class="segsel">${[1,2,3,4,5].map(v=>{const on=val===v,c=band(v/5*5);
      return `<button type="button" class="segbtn${on?' on':''}" ${on?`style="background:${c};border-color:${c};color:#fff"`:''} onclick="setDeliv(${o.id},'${esc(n).replace(/'/g,"\\'")}',${v})">${v}</button>`;}).join('')}
      <button type="button" class="segbtn${val==null?' on':''}" title="sem nota" onclick="setDeliv(${o.id},'${esc(n).replace(/'/g,"\\'")}','')">—</button></div>`;
  const rows=items.map(x=>{const av=x[tier==='advanced'?'adv':'std'];const val=o.deliv[x.n]!=null?o.deliv[x.n]:null;
    return `<div class="scard" style="margin-bottom:8px;display:grid;grid-template-columns:1fr 320px;gap:12px;align-items:center">
      <div><div style="font-size:14px;font-weight:600">${esc(x.n)}</div>
        <div class="mini" style="margin-top:2px">Disponibilidade no contratado: <b>${esc(av||'—')}</b></div></div>
      <div>${seg(x.n,val)}</div></div>`;}).join('');
  return `<div class="card"><h3>Contrato e nota dos entregáveis</h3><div class="pad">
      <div class="row" style="align-items:center"><div><label class="f">Plano contratado</label>
        <div class="toggle"><button class="${tier==='standard'?'on':''}" onclick="setTier(${o.id},'standard')">SOC Standard</button><button class="${tier==='advanced'?'on':''}" onclick="setTier(${o.id},'advanced')">SOC Advanced</button></div></div>
        <div style="margin-left:auto;text-align:right"><div class="f">Média das notas</div>
          <div style="font-size:24px;font-weight:600;color:${bandText(avg)}">${avg==null?'—':fmt1(avg)} <span style="font-size:12px;color:#94a3b8">/5</span></div></div></div>
      <p class="mini" style="margin:10px 0 0">São listados apenas os entregáveis que fazem sentido no plano <b>${tier==='advanced'?'SOC Advanced':'SOC Standard'}</b> (ex.: Health Check, Sala de Crise), conforme a matriz das propostas Viaconnect. Dê uma nota de 1 a 5 para cada um.</p></div></div>
    <h2>Entregáveis — ${tier==='advanced'?'SOC Advanced':'SOC Standard'} <span class="mini">(${items.length} itens)</span></h2>${rows}`;
}
function newCycle(orgId,slug){const n=asmsFor(orgId,slug).length+1,today=new Date().toISOString().slice(0,10);
  modal(`<div class="mh"><b>Novo ciclo</b><button class="btn ghost sm" style="margin-left:auto" onclick="closeModal()">×</button></div>
    <div class="mb"><div class="mini" style="margin-bottom:8px">${esc(FW[slug].name)}</div>
    <label class="f">Identificação</label><input id="cy" value="Ciclo ${n} — ${new Date().getFullYear()}"/><div style="height:8px"></div>
    <label class="f">Data de referência</label><input id="cd" type="date" value="${today}"/><div style="height:14px"></div>
    <button class="btn" onclick="createCycle(${orgId},'${slug}')">Criar ciclo</button></div>`);}
function createCycle(orgId,slug){const a={id:nid(),orgId,frameworkSlug:slug,cycle:document.getElementById('cy').value.trim()||'Ciclo',date:document.getElementById('cd').value,status:'in_progress',filledBy:null};
  db.assessments.push(a);db.answers[a.id]={};save();closeModal();go('run',{assessmentId:a.id,dIdx:0,aIdx:0});}
function delAsm(id){if(!confirm('Excluir este ciclo?'))return;db.assessments=db.assessments.filter(a=>a.id!==id);delete db.answers[id];save();render();}

// ===== Exportar / Importar assessment em XLSX (organização · domínio · nota · meta) =====
function assessmentRows(o,a){
  const fw=FW[a.frameworkSlug],A=ans(a.id),rows=[];
  fw.domains.forEach(function(d){d.aspects.forEach(function(asp){asp.questions.forEach(function(q){
    const av=A[q.code]||{};
    rows.push({'Organização':o.name,'Framework':fw.name,'Ciclo':a.cycle,'Domínio':d.name,
      'Aspecto':asp.name,'Código':q.code,'Item':q.text,
      'Nota':(av.cur==null?'':av.cur),'Meta':(av.tgt==null?'':av.tgt)});
  });});});
  return rows;
}
function exportXlsx(aid){
  const a=asmById(aid);if(!a)return;const o=orgById(a.orgId);
  if(typeof XLSX==='undefined'){alert('Biblioteca XLSX não carregada.');return;}
  const header=['Organização','Framework','Ciclo','Domínio','Aspecto','Código','Item','Nota','Meta'];
  const ws=XLSX.utils.json_to_sheet(assessmentRows(o,a),{header:header});
  ws['!cols']=[{wch:22},{wch:24},{wch:18},{wch:26},{wch:26},{wch:12},{wch:50},{wch:7},{wch:7}];
  const meta=XLSX.utils.aoa_to_sheet([['frameworkSlug','orgName','cycle','exportedAt'],
    [a.frameworkSlug,o.name,a.cycle,new Date().toISOString()]]);
  const wb=XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb,ws,'Assessment');
  XLSX.utils.book_append_sheet(wb,meta,'_meta');
  const safe=function(s){return String(s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^\w\-]+/g,'_').replace(/_+/g,'_').slice(0,40);};
  XLSX.writeFile(wb,'assessment_'+safe(o.name)+'_'+safe(a.frameworkSlug)+'_'+safe(a.cycle)+'.xlsx');
}
function importXlsx(orgId,file){
  if(typeof XLSX==='undefined'){alert('Biblioteca XLSX não carregada.');return;}
  const reader=new FileReader();
  reader.onload=function(e){
    try{
      const wb=XLSX.read(new Uint8Array(e.target.result),{type:'array'});
      const ws=wb.Sheets['Assessment']||wb.Sheets[wb.SheetNames[0]];
      if(!ws){alert('Planilha vazia ou inválida.');return;}
      const rows=XLSX.utils.sheet_to_json(ws,{defval:''});
      let slug=null,cycleName='Importado';
      if(wb.Sheets['_meta']){const m=(XLSX.utils.sheet_to_json(wb.Sheets['_meta'],{defval:''})[0])||{};
        if(m.frameworkSlug)slug=m.frameworkSlug;if(m.cycle)cycleName=String(m.cycle);}
      if((!slug||!FW[slug])&&rows[0]){const fn=rows[0]['Framework'];
        const hit=Object.keys(FW).find(function(s){return FW[s].name===fn;});if(hit)slug=hit;
        if(rows[0]['Ciclo'])cycleName=String(rows[0]['Ciclo']);}
      if(!slug||!FW[slug]){alert('Não consegui identificar o framework do arquivo (coluna "Framework" ou aba "_meta").');return;}
      const fw=FW[slug],valid={};
      fw.domains.forEach(function(d){d.aspects.forEach(function(asp){asp.questions.forEach(function(q){valid[q.code]=true;});});});
      const answers={};let n=0,ignored=0;
      rows.forEach(function(r){const code=String(r['Código']||'').trim();if(!code)return;
        if(!valid[code]){ignored++;return;}
        const cur=r['Nota'],meta=r['Meta'];
        answers[code]={cur:(cur===''||cur==null)?null:Number(cur),tgt:(meta===''||meta==null)?null:Number(meta)};n++;});
      if(!n){alert('Nenhum item válido encontrado para o framework "'+fw.name+'".');return;}
      const a={id:nid(),orgId:orgId,frameworkSlug:slug,cycle:cycleName+' (importado)',
        date:new Date().toISOString().slice(0,10),status:'in_progress',
        filledBy:(curUser()&&(curUser().name||curUser().username))||'import'};
      db.assessments.push(a);db.answers[a.id]=answers;
      const dd=dashboard(fw,answers);a.status=(dd.answered>=dd.total)?'completed':'in_progress';
      save();toast('Assessment importado em '+(orgById(orgId).name)+': '+n+' itens'+(ignored?(' ('+ignored+' ignorados)'):''));
      go('org',{orgId:orgId,orgTab:'assessment'});
    }catch(err){alert('Falha ao importar XLSX: '+((err&&err.message)||err));}
  };
  reader.readAsArrayBuffer(file);
}

// ===== run (sidebar navigation + segmented level selector) =====
function viewRun(){
  const a=asmById(state.assessmentId);if(!a)return go('orgs');
  const fw=FW[a.frameworkSlug],o=orgById(a.orgId),A=ans(a.id);
  if(state.dIdx>=fw.domains.length)state.dIdx=0;
  const d=fw.domains[state.dIdx]||fw.domains[0];if(state.aIdx>=d.aspects.length)state.aIdx=0;
  const asp=d.aspects[state.aIdx]||d.aspects[0];
  const dsAll=fw.domains.map(x=>domainScore(fw,x,A));
  const rail=`<div class="navrail no-print">${fw.domains.map((x,i)=>{const s=dsAll[i];const pct=s.total?Math.round(s.answered/s.total*100):0;const on=i===state.dIdx;
    return `<div class="navd"><button class="${on?'on':''}" onclick="go('run',{dIdx:${i},aIdx:0})"><span style="flex:0 0 auto">${esc(x.key)}</span><span class="pbar"><i style="width:${pct}%"></i></span><span class="mini" style="font-weight:400;flex:0 0 auto">${s.answered}/${s.total}</span></button>
      ${on?x.aspects.map((ap,j)=>{const as=aspectScore(fw,ap,A);return `<button class="navasp ${j===state.aIdx?'on':''}" onclick="go('run',{aIdx:${j}})">${esc(ap.name)} <span class="mini">(${as.answered}/${as.total})</span></button>`}).join(''):''}</div>`;}).join('')}</div>`;
  const matQ=asp.questions.filter(q=>q.type==='M'),capQ=asp.questions.filter(q=>q.type==='C');
  function group(title,qs,cls){if(!qs.length)return '';
    return `<div class="card"><h3><span class="qtype ${cls}">${cls}</span> ${title} <span class="badge">${qs.length} itens</span></h3><div class="pad">${qs.map(q=>qRow(fw,q,A)).join('')}</div></div>`;}
  return `<a onclick="go('org',{orgId:${o.id}})">← ${esc(o.name)}</a>
    <div class="row" style="align-items:center;margin-top:6px"><div style="flex:1"><h1>${esc(a.cycle)}</h1><p class="sub" style="margin:0">${esc(fw.name)} · ${esc(o.name)} · ${fw.scaleNote}</p></div>
      <button class="btn" onclick="saveRun(${a.id})">Salvar</button><button class="btn ghost" onclick="go('dashboard',{assessmentId:${a.id}})">Dashboard</button></div>
    <div class="dgrid" style="grid-template-columns:248px 1fr;align-items:start">${rail}
      <div><div class="row" style="align-items:center;margin-bottom:10px"><h2 style="margin:0">${esc(d.key)} › ${esc(asp.name)}</h2>
        <div style="margin-left:auto;display:flex;gap:6px" class="no-print"><button class="btn ghost sm" onclick="prevAsp(-1)">‹ Anterior</button><button class="btn ghost sm" onclick="prevAsp(1)">Próximo ›</button></div></div>
        ${group('Maturidade',matQ,'M')}${fw.opts.capability?group('Capability (cobertura)',capQ,'C'):''}</div></div>`;
}
function qRow(fw,q,A){const av=A[q.code]||{};
  let extra='';
  if(fw.opts.importance&&q.type==='M')extra+=`<div style="margin-top:10px"><label class="f">Importância</label>${impSel(q,av.imp)}</div>`;
  if(fw.opts.target)extra+=`<div style="margin-top:10px"><label class="f">Meta (nível desejado)</label>${sel(q,av.tgt,'tgt')}</div>`;
  return `<div class="qrow"><div><div class="qcode"><button class="help-btn" onclick="helpModal('${fw.slug}','${q.code}')">?</button>${esc(q.code)} <span class="qtype ${q.type}">${q.type}</span></div>
      <div class="qtext">${esc(q.text)}</div>${q.remark?`<div class="qremark">${esc(q.remark).slice(0,170)}</div>`:''}</div>
    <div><label class="f">Avaliação atual</label>${segHtml(q,av.cur)}${extra}</div></div>`;}
function curLevel(q,val){return q.levels.find(l=>l.v===val)||null;}
function segHtml(q,val){
  return `<div class="segsel">${q.levels.map(l=>{const on=val===l.v,c=band(l.v/q.scaleMax*5);
      return `<button type="button" class="segbtn${on?' on':''}" title="${esc(l.label)}${l.desc?' — '+esc(l.desc):''}" ${on?`style="background:${c};border-color:${c};color:#fff"`:''} onclick="setAns('${q.code}','cur',${l.v})">${l.v}</button>`;}).join('')}
      <button type="button" class="segbtn${val==null?' on':''}" title="não avaliado" onclick="setAns('${q.code}','cur','')">—</button></div>
    <div class="seglbl">${(function(){const l=curLevel(q,val);return l?('<b>'+esc(l.label)+'</b>'+(l.desc?' — '+esc(l.desc):'')):'<span class="mini">não avaliado</span>';})()}</div>`;
}
function sel(q,val,k){let h=`<select onchange="setAns('${q.code}','${k}',this.value)"><option value="">— não avaliado —</option>`;
  q.levels.forEach(l=>{h+=`<option value="${l.v}" ${val===l.v?'selected':''}>${l.v} · ${esc(l.label).slice(0,48)}</option>`;});return h+'</select>';}
function impSel(q,val){let h=`<select onchange="setAns('${q.code}','imp',this.value)">`;
  [1,2,3,4,5].forEach(v=>{const cur=(val||q.importance||3);h+=`<option value="${v}" ${cur===v?'selected':''}>${v} · ${IMP_LABEL[v]}</option>`;});return h+'</select>';}
function setAns(code,k,v){const A=db.answers[state.assessmentId]||(db.answers[state.assessmentId]={});const a=A[code]||(A[code]={cur:null,tgt:null});
  a[k]=(v===''||v==null)?null:Number(v);save();state._noscroll=true;render();}
function prevAsp(dir){const a=asmById(state.assessmentId),fw=FW[a.frameworkSlug];let di=state.dIdx,ai=state.aIdx+dir;
  if(ai<0){di--;if(di<0){di=fw.domains.length-1;}ai=fw.domains[di].aspects.length-1;}
  if(ai>=fw.domains[di].aspects.length){di++;if(di>=fw.domains.length)di=0;ai=0;}
  go('run',{dIdx:di,aIdx:ai});}
function saveRun(id){const a=asmById(id);a.filledBy=curUser().name||curUser().username;const fw=FW[a.frameworkSlug];const dd=dashboard(fw,ans(id));
  a.status=dd.answered>=dd.total?'completed':'in_progress';save();toast('Respostas salvas — preenchido por '+a.filledBy);}
function toast(m){const t=document.createElement('div');t.textContent=m;t.style.cssText='position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#0f172a;color:#fff;padding:10px 16px;border-radius:8px;z-index:99;font-size:14px';document.body.appendChild(t);setTimeout(()=>t.remove(),2200);}

// ===== dashboard (refactored: ECharts, card hierarchy, 0–5 scale) =====
function setRadar(m){state.radarMode=m;render();}
function viewDashboard(){
  const a=asmById(state.assessmentId);if(!a)return go('orgs');
  const fw=FW[a.frameworkSlug],o=orgById(a.orgId),dd=dashboard(fw,ans(a.id)),isSoc=fw.kind==='soc-cmm';
  const hasCap=isSoc&&dd.domains.some(d=>d.hasCapability);
  const head=`<div class="no-print"><a onclick="go('org',{orgId:${o.id}})">← ${esc(o.name)}</a>
    <div class="row" style="align-items:center;margin-top:6px"><div style="flex:1"><h1>${esc(a.cycle)} · Dashboard</h1>
      <p class="sub" style="margin:0">${esc(fw.name)} · ${esc(o.name)}</p></div>
      <button class="btn ghost" onclick="go('run',{assessmentId:${a.id},dIdx:0,aIdx:0})">Preencher</button>
      <button class="btn" onclick="exportPdf()">⤓ Exportar PDF</button></div></div>`;
  // empty state
  if(dd.answered===0)return head+`<div class="card"><div class="empty">
      <div style="font-size:42px;color:#cbd5e1">◔</div><h3 style="border:0;justify-content:center">Nenhum item avaliado ainda</h3>
      <p class="mini" style="max-width:360px;margin:6px auto 14px">Comece a preencher as respostas para ver o score consolidado, o ranking de domínios e os gráficos.</p>
      <button class="btn" onclick="go('run',{assessmentId:${a.id},dIdx:0,aIdx:0})">Começar a preencher</button></div></div>`;
  // 0–5 model
  const D=dd.domains.map(d=>({key:d.key,full:d.name,score:d.mpct==null?null:d.mpct/100*5,cap:d.cpct==null?null:d.cpct/100*3,
    target:d.tpct==null?null:d.tpct/100*5,answered:d.answered,total:d.total,assessed:d.answered>0,aspects:d.aspects,hasCapability:d.hasCapability}));
  const overall=dd.overall==null?null:dd.overall/100*5, overallTgt=dd.overallTarget==null?null:dd.overallTarget/100*5;
  const assessed=D.filter(d=>d.assessed), naCount=D.length-assessed.length;
  const best=assessed.slice().sort((x,y)=>y.score-x.score)[0], worst=assessed.slice().sort((x,y)=>x.score-y.score)[0];
  // KPIs
  const kpi=`<div class="dgrid" style="grid-template-columns:1fr 1fr">
    <div class="kpi"><div class="k">domínios avaliados</div><div class="v">${assessed.length} / ${D.length}</div></div>
    <div class="kpi"><div class="k">cobertura de itens</div><div class="v">${Math.round(dd.answered/dd.total*100)}%</div><div class="mini">${dd.answered}/${dd.total}</div></div>
    <div class="kpi"><div class="k">maior maturidade</div><div class="v" style="font-size:15px;color:${best?bandText(best.score):'#64748b'}">${best?esc(best.key)+' · '+fmt1(best.score):'—'}</div></div>
    <div class="kpi"><div class="k">${hasCap?'capability geral':'menor maturidade'}</div><div class="v" style="font-size:15px;color:${hasCap?'#6d28d9':(worst?bandText(worst.score):'#64748b')}">${hasCap?(dd.overallCap==null?'—':fmt1(dd.overallCap/100*3)+' / 3'):(worst?esc(worst.key)+' · '+fmt1(worst.score):'—')}</div></div>
  </div>`;
  // ranking
  const ranked=D.slice().sort((x,y)=>(y.assessed-x.assessed)||((y.score||0)-(x.score||0)));
  const rankItems=ranked.map(d=>({name:d.key,full:d.full,score:d.score,target:d.target,assessed:d.assessed}));
  const rankH=Math.max(170,ranked.length*30+30);
  // radar (assessed-only, domain level) + optional aspect toggle (SOC print radar)
  const rMode=state.radarMode||'dom';
  const radarItems=assessed.map(d=>({name:d.key,full:d.full,score:d.score,cap:d.cap}));
  const radarBody = (isSoc&&rMode==='asp') ? socRadar(dd.domains)
    : (radarItems.length>=3 ? ec('ec-radar',360,ecRadar(radarItems,hasCap))
       : `<div class="empty mini">Radar disponível a partir de 3 domínios avaliados.</div>`)
      + (naCount?`<div class="mini" style="text-align:center;margin-top:4px">${naCount} domínio(s) não avaliado(s) fora do radar</div>`:'');
  // per-domain score cards
  const cards=D.map(d=>d.assessed?`<div class="scard" title="${esc(d.full)}">
      <div class="mini" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600;color:#334155">${esc(d.key)}</div>
      <div style="font-size:24px;font-weight:600;color:${bandText(d.score)}">${fmt1(d.score)} <span style="font-size:12px;color:#94a3b8">/5</span></div>
      <span class="lvlpill" style="background:${bandSoft(d.score)};color:${bandText(d.score)}">${levelName(d.score)}</span>
      <div class="seg">${[0,1,2,3,4].map(k=>`<span style="background:${k<Math.round(d.score)?band(d.score):'#e2e8f0'}"></span>`).join('')}</div>
      <div class="mini" style="margin-top:6px">cobertura ${d.answered}/${d.total}${hasCap&&d.hasCapability?` · cap ${d.cap==null?'—':fmt1(d.cap)+'/3'}`:''}</div></div>`
    :`<div class="scard na" title="${esc(d.full)}"><div class="mini" style="font-weight:600;color:#334155">${esc(d.key)}</div>
      <div style="font-size:14px;color:#94a3b8;margin-top:8px">— não avaliado</div>
      <div class="mini" style="margin-top:18px">0/${d.total} itens</div></div>`).join('');
  // evolution
  const cycles=asmsFor(a.orgId,a.frameworkSlug).sort((x,y)=>(x.date||'').localeCompare(y.date||''));
  const evo=cycles.map(c=>{const dc=dashboard(fw,ans(c.id));return {label:c.cycle.split('—')[0].trim().slice(0,14),score:dc.overall==null?null:dc.overall/100*5};});
  // per-domain detail of SUBDOMAINS — collapsible card with Radar|Barras toggle (shared data + color scale)
  state.detailMode=state.detailMode||{};
  const doms=D.map((s,i)=>{if(!s.assessed)return '';
    const open=state.openDomains[i]||state._printAll;
    const mode=state.detailMode[s.key]||'radar';
    const views=s.aspects.map(x=>({code:x.code,full:x.name,score:x.matScore,assessed:x.answered>0}));
    const nAssessed=views.filter(v=>v.assessed).length;
    let chart='';
    if(open){
      const useRadar=mode==='radar'&&nAssessed>=3;
      chart=ec('det-'+i, useRadar?320:Math.max(150,views.length*26+34),
        useRadar?ecSubRadar(views,band(s.score)):ecSubBars(views,s.score));
      if(mode==='radar'&&nAssessed<3)chart=`<div class="mini" style="margin-bottom:6px">Radar requer ≥3 subdomínios avaliados — mostrando barras.</div>`+chart;
    }
    return `<div class="card"><div class="domhead" onclick="toggleDom(${i})"><span class="chev ${open?'open':''}">▶</span><b>${esc(s.key)}</b>
        <span class="mini">${esc(s.full).slice(0,60)} · ${views.length} subdomínios</span>
        <span style="margin-left:auto" class="lvlpill" style="background:${bandSoft(s.score)};color:${bandText(s.score)}">${fmt1(s.score)} · ${levelName(s.score)}</span></div>
      ${open?`<div class="domdetail"><div class="pad" style="padding-top:0">
        <div class="no-print" style="display:flex;margin-bottom:8px"><div class="toggle"><button class="${mode==='radar'?'on':''}" onclick="setDetail('${esc(s.key)}','radar')">Radar</button><button class="${mode!=='radar'?'on':''}" onclick="setDetail('${esc(s.key)}','bars')">Barras</button></div></div>
        ${chart}</div></div>`:''}</div>`;}).join('');

  return head
    +`<div class="dgrid" style="grid-template-columns:300px 1fr;margin-bottom:16px">
        <div class="card"><h3>Maturidade geral</h3><div class="pad" style="padding-top:4px">${ec('ec-gauge',180,ecGauge(overall,overallTgt))}
          <div style="text-align:center;margin-top:-6px"><span class="lvlpill" style="background:${bandSoft(overall)};color:${bandText(overall)}">${levelName(overall)}</span>
          <div class="mini" style="margin-top:6px">${dd.answered}/${dd.total} itens${overallTgt!=null?` · meta ${fmt1(overallTgt)}`:''}</div></div></div></div>
        <div class="card"><h3>Resumo</h3><div class="pad">${kpi}</div></div></div>
     <div class="dgrid" style="grid-template-columns:1.25fr 1fr;margin-bottom:16px">
        <div class="card"><h3><i></i>Ranking de domínios <span class="mini" style="font-weight:400">· 0–5, ordenado</span></h3><div class="pad">${ec('ec-rank',rankH,ecRanking(rankItems,overall))}</div></div>
        <div class="card"><h3>Radar — shape ${isSoc?`<div class="toggle no-print"><button class="${rMode==='dom'?'on':''}" onclick="setRadar('dom')">Domínios</button><button class="${rMode==='asp'?'on':''}" onclick="setRadar('asp')">Aspectos</button></div>`:''}</h3><div class="pad">${radarBody}</div></div></div>
     <div class="card"><h3>Score por domínio <span class="mini" style="font-weight:400">· nível 0–5</span></h3><div class="pad">
        <div class="dgrid" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">${cards}</div></div></div>
     ${cycles.length?`<div class="card"><h3>Evolução por ciclo <span class="mini" style="font-weight:400">· maturidade geral (0–5)</span></h3><div class="pad">${ec('ec-evo',210,ecEvolution(evo))}</div></div>`:''}
     <h2 class="no-print">Detalhe por domínio <span class="mini">(clique para abrir · alterne Radar/Barras)</span></h2>${doms}`;
}
function toggleDom(i){state.openDomains[i]=!state.openDomains[i];render();}
function setDetail(key,mode){state.detailMode=state.detailMode||{};state.detailMode[key]=mode;render();}
function exportPdf(){state._printAll=true;render();setTimeout(function(){window.print();state._printAll=false;render();},500);}

// ===== config =====
function viewConfig(){if(curUser().role!=='admin')return go('orgs');
  const orgRows=db.orgs.map(o=>`<tr><td>${esc(o.name)}</td><td>${esc(o.sector||'—')}</td><td>${asmsFor(o.id).length}</td><td style="text-align:right"><button class="btn danger sm" onclick="cfgDelOrg(${o.id})">Excluir</button></td></tr>`).join('');
  const userRows=db.users.map(u=>`<tr><td><b>${esc(u.username)}</b></td><td>${esc(u.name||'—')}</td><td><span class="badge ${u.role==='admin'?'b':''}">${u.role}</span></td>
    <td style="text-align:right;white-space:nowrap"><button class="btn ghost sm" onclick="cfgPwd(${u.id})">Senha</button>${u.username==='admin'?'':`<button class="btn danger sm" onclick="cfgDelUser(${u.id})">Excluir</button>`}</td></tr>`).join('');
  const cl=db.claude||{};const MODELS=[['claude-opus-4-8','Claude Opus 4.8 (recomendado)'],['claude-sonnet-4-6','Claude Sonnet 4.6'],['claude-haiku-4-5','Claude Haiku 4.5'],['claude-fable-5','Claude Fable 5']];
  const claudeCard=`<div class="card"><h3>Integração com Claude (IA) <span class="badge ${cl.apiKey?'g':''}">${cl.apiKey?'configurada':'não configurada'}</span></h3><div class="pad">
      <p class="mini" style="margin:0 0 12px">Conecta a aba <b>Recomendações</b> à API do Claude para gerar recomendações sob medida a partir do resultado do assessment de Domínios. A "skill" enviada já vem alimentada com os frameworks e a matriz de entregáveis Viaconnect. A chave fica salva apenas neste navegador (localStorage) e as chamadas vão direto para api.anthropic.com.</p>
      <div class="row">
        <div style="flex:2;min-width:260px"><label class="f">Chave da API (x-api-key)</label><input id="clk" type="password" placeholder="sk-ant-..." value="${esc(cl.apiKey||'')}"/></div>
        <div style="flex:1;min-width:190px"><label class="f">Modelo</label><select id="clm">${MODELS.map(m=>`<option value="${m[0]}" ${(cl.model||'claude-opus-4-8')===m[0]?'selected':''}>${m[1]}</option>`).join('')}</select></div>
      </div>
      <div style="margin-top:10px"><label class="f">Instruções adicionais para a skill (opcional)</label><textarea id="clx" rows="3" placeholder="Ex.: priorize requisitos regulatórios ANPD/BACEN; dê ênfase à redução de MTTR.">${esc(cl.extra||'')}</textarea></div>
      <div class="row" style="margin-top:12px;align-items:center"><button class="btn" onclick="cfgSaveClaude()">Salvar integração</button>${cl.apiKey?`<button class="btn ghost" onclick="cfgTestClaude()">Testar conexão</button><button class="btn danger" onclick="cfgClearClaude()">Remover chave</button>`:''}<span id="cltest" class="mini"></span></div>
    </div></div>`;
  return `<h1>Configurações</h1><p class="sub">Administração de organizações, usuários internos e integração com a IA.</p>
    <div class="grid" style="grid-template-columns:1fr 1fr">
      <div class="card"><h3>Organizações</h3><div class="pad"><div class="row"><div style="flex:1"><label class="f">Nova organização</label><input id="cfgon"/></div><div style="flex:1"><label class="f">Setor</label><input id="cfgos"/></div><button class="btn" onclick="cfgAddOrg()">Criar</button></div><div style="height:12px"></div><table><tr><th>Nome</th><th>Setor</th><th>Aval.</th><th></th></tr>${orgRows||'<tr><td colspan=4 class="mini">Nenhuma</td></tr>'}</table></div></div>
      <div class="card"><h3>Usuários</h3><div class="pad"><div class="row"><div><label class="f">Usuário</label><input id="cfgu"/></div><div><label class="f">Nome</label><input id="cfgn"/></div></div>
        <div class="row" style="margin-top:8px"><div><label class="f">Senha</label><input id="cfgp" type="password"/></div><div><label class="f">Perfil</label><select id="cfgr"><option value="user">user</option><option value="admin">admin</option></select></div><button class="btn" onclick="cfgAddUser()">Criar</button></div>
        <div style="height:12px"></div><table><tr><th>Usuário</th><th>Nome</th><th>Perfil</th><th></th></tr>${userRows}</table></div></div></div>
    ${claudeCard}`;}
function cfgSaveClaude(){db.claude={apiKey:document.getElementById('clk').value.trim(),model:document.getElementById('clm').value,extra:document.getElementById('clx').value.trim()};save();toast('Integração Claude salva');state._noscroll=true;render();}
function cfgClearClaude(){if(!confirm('Remover a chave e as configurações do Claude?'))return;db.claude={};save();state._noscroll=true;render();}
async function cfgTestClaude(){const el=document.getElementById('cltest');const cfg=db.claude||{};if(!cfg.apiKey){el.textContent='Salve a chave antes de testar.';return;}el.style.color='#64748b';el.textContent='Testando…';
  try{const res=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',headers:{'content-type':'application/json','x-api-key':cfg.apiKey,'anthropic-version':'2023-06-01','anthropic-dangerous-direct-browser-access':'true'},body:JSON.stringify({model:cfg.model||'claude-opus-4-8',max_tokens:16,messages:[{role:'user',content:'responda apenas: ok'}]})});
    const d=await res.json();if(!res.ok)throw new Error((d.error&&d.error.message)||('HTTP '+res.status));
    el.style.color='#16a34a';el.textContent='✓ Conexão OK ('+(d.model||cfg.model)+')';}
  catch(e){el.style.color='#dc2626';el.textContent='✗ '+((e&&e.message)||e);}}
function cfgAddOrg(){const n=document.getElementById('cfgon').value.trim();if(!n)return;db.orgs.push({id:nid(),name:n,sector:document.getElementById('cfgos').value.trim()});save();render();}
function cfgDelOrg(id){if(!confirm('Excluir a organização e TODAS as suas avaliações?'))return;db.orgs=db.orgs.filter(o=>o.id!==id);const rm=db.assessments.filter(a=>a.orgId===id).map(a=>a.id);db.assessments=db.assessments.filter(a=>a.orgId!==id);rm.forEach(i=>delete db.answers[i]);save();render();}
function cfgAddUser(){const u=document.getElementById('cfgu').value.trim(),p=document.getElementById('cfgp').value;if(!u||!p)return;if(db.users.some(x=>x.username===u)){alert('Usuário já existe');return}db.users.push({id:nid(),username:u,name:document.getElementById('cfgn').value.trim(),password:p,role:document.getElementById('cfgr').value});save();render();}
function cfgDelUser(id){if(!confirm('Excluir usuário?'))return;db.users=db.users.filter(u=>u.id!==id);save();render();}
function cfgPwd(id){const u=db.users.find(x=>x.id===id);modal(`<div class="mh"><b>Alterar senha — ${esc(u.username)}</b><button class="btn ghost sm" style="margin-left:auto" onclick="closeModal()">×</button></div><div class="mb"><label class="f">Nova senha</label><input id="np" type="password"/><div style="height:12px"></div><button class="btn" onclick="cfgSetPwd(${id})">Salvar</button></div>`);}
function cfgSetPwd(id){const v=document.getElementById('np').value;if(!v)return;db.users.find(x=>x.id===id).password=v;save();closeModal();toast('Senha alterada');}

// ===== shell =====
function render(){const root=document.getElementById('root');
  if(state.view==='login'||!db.session){root.innerHTML=viewLogin();return;}
  const u=curUser();const navItems=[['orgs','Organizações']].concat(u.role==='admin'?[['config','Configurações']]:[]);
  const header=`<header><div class="bar"><div class="logo"><span class="dot"></span>Viaconnect SOC <span style="font-weight:400;color:var(--mut);font-size:12px">Health Check</span></div>
    <nav>${navItems.map(([v,l])=>`<button class="${state.view===v||(v==='orgs'&&['org','run','dashboard'].includes(state.view))?'active':''}" onclick="go('${v}')">${l}</button>`).join('')}</nav>
    <div class="right"><span>${esc(u.name||u.username)} <span class="badge ${u.role==='admin'?'b':''}">${u.role}</span></span><button class="btn ghost sm" onclick="logout()">Sair</button></div></div></header>`;
  let body={orgs:viewOrgs,org:viewOrg,run:viewRun,dashboard:viewDashboard,config:viewConfig}[state.view];
  body=body?body():viewOrgs();
  const sy=window.scrollY;
  root.innerHTML=header+'<main>'+body+'</main>';
  flushCharts();ensureResize();
  if(state._noscroll){state._noscroll=false;window.scrollTo(0,sy);}else{window.scrollTo(0,0);}}
// Bootstrap: tenta carregar o estado do backend (Postgres); se não houver API
// (preview.html aberto solto), cai para localStorage. Depois renderiza.
(async function boot(){
  try{
    const res=await fetch('/api/state',{cache:'no-store'});
    if(res.ok){
      const remote=await res.json();
      if(remote&&remote.users){const lc=db.claude;db=remote;if(lc)db.claude=lc;persistLocal();}
      else{const payload=Object.assign({},db);delete payload.claude;
        fetch('/api/state',{method:'PUT',headers:{'content-type':'application/json'},body:JSON.stringify(payload)}).catch(function(){});}
    }else{BACKEND=false;}
  }catch(e){BACKEND=false;}
  render();
})();
</script></body></html>
"""
# Emite um frontend MODULAR (app web real, não um HTML único): o template
# monolítico é dividido em index.html + app.js + data.js + echarts.min.js,
# servidos por Nginx. A persistência vai para o backend (PostgreSQL via /api).
WEB = os.path.join(HERE, "web")
os.makedirs(WEB, exist_ok=True)
MARK = "<script>__ECHARTS__</script>"
head_html, after = TEMPLATE.split(MARK, 1)
app_js = after.split("<script>", 1)[1].rsplit("</script></body></html>", 1)[0]
app_js = app_js.replace("const DATA = __DATA__;", "const DATA = window.DATA;")
index_html = (head_html
              + '<script src="echarts.min.js"></script>\n'
              + '<script src="xlsx.full.min.js"></script>\n'
              + '<script src="data.js"></script>\n'
              + '<script src="app.js"></script>\n'
              + '</body></html>\n')
with open(os.path.join(WEB, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
with open(os.path.join(WEB, "app.js"), "w", encoding="utf-8") as f:
    f.write(app_js)
with open(os.path.join(WEB, "data.js"), "w", encoding="utf-8") as f:
    f.write("window.DATA = " + data_json + ";\n")
shutil.copyfile(os.path.join(HERE, "assets", "echarts.min.js"), os.path.join(WEB, "echarts.min.js"))
shutil.copyfile(os.path.join(HERE, "assets", "xlsx.full.min.js"), os.path.join(WEB, "xlsx.full.min.js"))
for fn in ("index.html", "app.js", "data.js", "echarts.min.js", "xlsx.full.min.js"):
    print(f"  web/{fn}: {round(os.path.getsize(os.path.join(WEB, fn))/1024)} KB")
print("wrote modular frontend into web/")

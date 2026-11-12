import streamlit as st
import json, random, sqlite3, math
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
DB = ROOT / "database" / "progress.db"
DB.parent.mkdir(exist_ok=True)
QUESTIONS = json.loads((ROOT/"data"/"questions.json").read_text(encoding="utf-8"))
SUBJECTS = json.loads((ROOT/"data"/"subjects.json").read_text(encoding="utf-8"))

st.set_page_config(page_title="CEM Prep | Certified Energy Manager", page_icon="⚡", layout="wide")
st.markdown("""
<style>
.main {background:#f6f8fb}
.block-container {padding-top:1.4rem;max-width:1250px}
.hero {background:linear-gradient(120deg,#153653,#24607a);padding:1.5rem 1.8rem;border-radius:16px;color:white}
.hero h1,.hero p {color:white}
</style>
""", unsafe_allow_html=True)

def db():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS attempts(
        id INTEGER PRIMARY KEY AUTOINCREMENT, qid TEXT, subject TEXT, correct INTEGER,
        chosen INTEGER, ts TEXT, mode TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, note TEXT, ts TEXT)""")
    c.commit()
    return c

def save_attempt(q, chosen, mode):
    c=db()
    c.execute("INSERT INTO attempts(qid,subject,correct,chosen,ts,mode) VALUES(?,?,?,?,?,?)",
              (q["id"],q["subject"],int(chosen==q["answer"]),chosen,datetime.now().isoformat(timespec="seconds"),mode))
    c.commit(); c.close()

def stats():
    c=db()
    rows=c.execute("SELECT COUNT(*), COALESCE(SUM(correct),0) FROM attempts").fetchone()
    by=c.execute("SELECT subject,COUNT(*),SUM(correct) FROM attempts GROUP BY subject").fetchall()
    c.close()
    return rows, {r[0]:(r[1],r[2]) for r in by}

def question_pool(subject="All subjects", difficulty="All", missed_only=False):
    pool=QUESTIONS[:]
    if subject!="All subjects": pool=[q for q in pool if q["subject"]==subject]
    if difficulty!="All": pool=[q for q in pool if q["difficulty"]==difficulty]
    if missed_only:
        c=db(); missed={r[0] for r in c.execute("SELECT qid FROM attempts WHERE correct=0").fetchall()}; c.close()
        pool=[q for q in pool if q["id"] in missed]
    return pool

def formula_library():
    return [
    ("Electrical","Single-phase real power","P = V × I × PF","kW = V × A × PF ÷ 1,000"),
    ("Electrical","Three-phase real power","P = √3 × VLL × I × PF","kW = 1.732 × line voltage × line current × PF ÷ 1,000"),
    ("Electrical","Apparent power","kVA = kW ÷ PF","PF = kW ÷ kVA"),
    ("Energy accounting","Load factor","LF = kWh ÷ (peak kW × hours)","Use hours in the actual billing period"),
    ("Energy accounting","Energy intensity","Energy use ÷ floor area or production","State units and normalization basis"),
    ("HVAC","Cooling capacity","1 refrigeration ton = 12,000 Btu/hr","kW cooling = tons × 3.517"),
    ("HVAC","COP","COP = useful thermal output ÷ energy input","Use consistent energy units"),
    ("HVAC","Chiller specific power","kW/ton = input kW ÷ cooling tons","Lower is generally better at comparable conditions"),
    ("Thermal","Btu to kWh","1 kWh = 3,412.142 Btu","1 therm = 100,000 Btu"),
    ("Thermal","Natural gas","1 CCF ≈ 100 cubic feet","Energy content varies by utility and billing basis"),
    ("Motors","Horsepower conversion","1 hp = 0.746 kW","Input kW = hp × 0.746 ÷ efficiency"),
    ("Lighting","Lighting energy savings","ΔkW × operating hours = kWh saved","ΔkW = watts reduced ÷ 1,000"),
    ("Boilers","Combustion efficiency","Useful heat output ÷ fuel input","Use consistent heating-value basis"),
    ("Economics","Simple payback","Initial cost ÷ annual savings","Does not account for time value of money"),
    ("Economics","Net present value","NPV = Σ[CFt ÷ (1+r)^t] − initial cost","Use consistent nominal/real assumptions"),
    ("M&V","Savings","Adjusted baseline energy − reporting-period energy","Document boundaries and adjustments"),
    ("Renewables","Capacity factor","Actual energy ÷ (rated power × hours)","Express as a percentage"),
    ("Storage","Round-trip efficiency","Discharged energy ÷ charged energy","Define AC/DC boundary and test conditions"),
    ("Pumping","Hydraulic power","Power depends on flow, head, fluid density, and efficiency","Use consistent units and fluid properties"),
    ("Steam","Condensate recovery","Compare recovered heat and water value with system costs","Account for return temperature and quality")
    ]

st.sidebar.markdown("## ⚡ CEM PREP")
st.sidebar.caption("Certified Energy Manager training")
page=st.sidebar.radio("Navigate",["Dashboard","Study & Practice","Exam Simulator","Calculation Lab","Formula Library","Performance & Notes","About"])
st.sidebar.divider()
st.sidebar.caption(f"{len(QUESTIONS):,} original practice questions")
st.sidebar.caption("Independent study tool • Not AEE endorsed")

if page=="Dashboard":
    total, by=stats()
    st.markdown('<div class="hero"><h1>Certified Energy Manager Prep</h1><p>Study smarter. Solve technical problems. Build exam readiness.</p></div>',unsafe_allow_html=True)
    st.write("")
    a,b,c,d=st.columns(4)
    a.metric("Question bank",f"{len(QUESTIONS):,}")
    b.metric("Questions attempted",f"{total[0]:,}")
    c.metric("Correct answers",f"{total[1]:,}")
    d.metric("Overall accuracy",f"{(100*total[1]/total[0]):.1f}%" if total[0] else "—")
    st.subheader("CEM subject areas")
    for s in SUBJECTS:
        count=sum(1 for q in QUESTIONS if q["subject"]==s["name"])
        attempted,correct=by.get(s["name"],(0,0))
        col1,col2,col3=st.columns([5,1,2])
        col1.write(s["name"]); col2.write(f"{s['weight_percent']}%")
        col3.progress(correct/attempted if attempted else 0,text=f"{correct}/{attempted} correct" if attempted else "Not attempted")
    st.info("Suggested routine: study one subject, complete a practice set, then review every missed question and calculation.")
    st.caption("Subject percentages are planning allocations configured for this app. Confirm the current AEE candidate handbook for official exam specifications.")

elif page=="Study & Practice":
    st.title("Study & Practice")
    subjects=["All subjects"]+[s["name"] for s in SUBJECTS]
    c1,c2,c3=st.columns(3)
    subject=c1.selectbox("Subject",subjects)
    difficulty=c2.selectbox("Difficulty",["All","Foundational","Intermediate","Advanced"])
    mode=c3.selectbox("Question pool",["All questions","Missed questions"])
    pool=question_pool(subject,difficulty,mode=="Missed questions")
    st.caption(f"{len(pool):,} questions available.")
    if "practice" not in st.session_state or st.button("Start / reshuffle practice set"):
        if pool:
            st.session_state.practice={"items":random.sample(pool,min(20,len(pool))),"idx":0,"done":{}}
        else: st.warning("No missed questions match this filter yet.")
    if "practice" in st.session_state and st.session_state.practice["items"]:
        p=st.session_state.practice; q=p["items"][p["idx"]]
        st.progress((p["idx"]+1)/len(p["items"]),text=f"Question {p['idx']+1} of {len(p['items'])}")
        st.markdown(f"**{q['subject']}** · {q['topic']} · {q['difficulty']}")
        st.subheader(q["question"])
        key=f"ans_{q['id']}_{p['idx']}"
        choice=st.radio("Select one answer",q["options"],index=None,key=key)
        if st.button("Check answer",type="primary",disabled=choice is None):
            selected=q["options"].index(choice)
            if key not in p["done"]:
                p["done"][key]=selected; save_attempt(q,selected,"Practice")
            if selected==q["answer"]: st.success("Correct")
            else: st.error(f"Incorrect. Correct answer: {q['options'][q['answer']]}")
            st.info(q["explanation"])
            if q.get("formula"): st.code(q["formula"])
        if key in p["done"]:
            selected=p["done"][key]
            st.caption("Answer recorded.")
            left,right=st.columns(2)
            if left.button("Previous",disabled=p["idx"]==0): p["idx"]-=1; st.rerun()
            if right.button("Next question",type="primary",disabled=p["idx"]>=len(p["items"])-1): p["idx"]+=1; st.rerun()

elif page=="Exam Simulator":
    st.title("Exam Simulator")
    st.warning("Practice simulation only. Confirm live exam format, timing, and scoring with the current AEE candidate handbook.")
    if "exam" not in st.session_state: st.session_state.exam=None
    if st.session_state.exam is None:
        x,y,z=st.columns(3)
        n=x.selectbox("Question count",[25,50,65,100,130],index=4)
        dur=y.selectbox("Suggested time (minutes)",[60,90,120,180,240],index=4)
        scope=z.selectbox("Scope",["All subjects"]+[s["name"] for s in SUBJECTS])
        if st.button("Generate examination",type="primary"):
            pool=question_pool(scope)
            items=random.sample(pool,min(n,len(pool)))
            st.session_state.exam={"items":items,"index":0,"answers":{},"submitted":False,"duration":dur}
            st.rerun()
    ex=st.session_state.exam
    if ex:
        if not ex["submitted"]:
            items=ex["items"]; i=ex["index"]; q=items[i]
            st.progress((i+1)/len(items),text=f"Question {i+1} of {len(items)}")
            st.caption(f"{q['subject']} · {q['difficulty']}")
            st.subheader(q["question"])
            prior=ex["answers"].get(q["id"])
            pick=st.radio("Choose an answer",q["options"],index=prior,key=f"exam_{q['id']}")
            c1,c2,c3=st.columns(3)
            if c1.button("Save answer"):
                ex["answers"][q["id"]]=q["options"].index(pick); st.toast("Answer saved")
            if c2.button("Previous",disabled=i==0): ex["index"]-=1; st.rerun()
            if c3.button("Next",disabled=i==len(items)-1): ex["index"]+=1; st.rerun()
            st.caption(f"Answered: {len(ex['answers'])} / {len(items)} · Suggested time: {ex['duration']} minutes")
            if st.button("Submit examination",type="primary"):
                ex["submitted"]=True
                for item in items:
                    if item["id"] in ex["answers"]: save_attempt(item,ex["answers"][item["id"]],"Exam")
                st.rerun()
        else:
            correct=sum(ex["answers"].get(q["id"],-1)==q["answer"] for q in ex["items"])
            score=100*correct/len(ex["items"])
            st.metric("Practice score",f"{score:.1f}%",f"{correct} of {len(ex['items'])} correct")
            st.progress(score/100)
            st.subheader("Answer review")
            for q in ex["items"]:
                chosen=ex["answers"].get(q["id"],-1)
                with st.expander(f"{q['id']} · {'Correct' if chosen==q['answer'] else 'Review'} · {q['subject']}"):
                    st.write(q["question"])
                    st.write("Your answer: "+(q["options"][chosen] if chosen>=0 else "Not answered"))
                    st.write("Correct answer: "+q["options"][q["answer"]])
                    st.write(q["explanation"])
            if st.button("Finish and clear exam"):
                st.session_state.exam=None; st.rerun()

elif page=="Calculation Lab":
    st.title("Engineering Calculation Lab")
    st.caption("Educational estimates. Validate units, assumptions, tariff provisions, and equipment data for real projects.")
    tab1,tab2,tab3,tab4=st.tabs(["Electrical","HVAC & Thermal","Energy & Demand","Project Economics"])
    with tab1:
        st.subheader("Balanced three-phase power")
        v=st.number_input("Line voltage (V)",value=480.0,min_value=0.0)
        amps=st.number_input("Line current (A)",value=100.0,min_value=0.0)
        pf=st.slider("Power factor",0.1,1.0,0.90)
        st.metric("Real power",f"{math.sqrt(3)*v*amps*pf/1000:,.2f} kW")
        st.metric("Apparent power",f"{math.sqrt(3)*v*amps/1000:,.2f} kVA")
        hp=st.number_input("Motor output (hp)",value=50.0,min_value=0.0)
        eff=st.slider("Motor efficiency",0.50,0.99,0.92)
        st.metric("Estimated motor input",f"{hp*0.746/eff:,.2f} kW")
    with tab2:
        tons=st.number_input("Chiller capacity (tons)",value=100.0,min_value=0.0)
        kwton=st.number_input("Chiller specific power (kW/ton)",value=0.70,min_value=0.0)
        st.metric("Electrical demand",f"{tons*kwton:,.2f} kW")
        st.metric("Cooling capacity",f"{tons*3.517:,.2f} kW thermal")
        st.metric("Approximate COP",f"{3.517/kwton:,.2f}" if kwton else "—")
        btu=st.number_input("Thermal energy (Btu)",value=100000.0,min_value=0.0)
        st.metric("Equivalent kWh thermal",f"{btu/3412.142:,.3f}")
        st.metric("Equivalent therms",f"{btu/100000:,.3f}")
        ccf=st.number_input("Natural gas volume (CCF)",value=10.0,min_value=0.0)
        heat=st.number_input("Assumed gas heat content (Btu/CCF)",value=100000.0,min_value=0.0)
        st.metric("Estimated gas energy",f"{ccf*heat/100000:,.2f} therms")
    with tab3:
        demand=st.number_input("Peak demand (kW)",value=500.0,min_value=0.0)
        energy=st.number_input("Energy use (kWh)",value=180000.0,min_value=0.0)
        hours=st.number_input("Hours in period",value=720.0,min_value=1.0)
        st.metric("Load factor",f"{100*energy/(demand*hours):.2f}%" if demand else "—")
        st.caption("If load factor exceeds 100%, check the demand and interval definitions.")
    with tab4:
        cost=st.number_input("Project cost ($)",value=100000.0,min_value=0.0)
        savings=st.number_input("Annual cost savings ($/yr)",value=25000.0,min_value=0.0)
        st.metric("Simple payback",f"{cost/savings:.2f} years" if savings else "—")
        rate=st.number_input("Discount rate (%)",value=7.0,min_value=0.0,max_value=100.0)/100
        life=st.number_input("Study life (years)",value=15,min_value=1,max_value=60)
        annual=st.number_input("Annual net cash flow ($)",value=25000.0)
        npv=sum(annual/((1+rate)**t) for t in range(1,life+1))-cost
        st.metric("NPV",f"${npv:,.2f}")

elif page=="Formula Library":
    st.title("Formula Library")
    formulas=formula_library(); categories=sorted(set(x[0] for x in formulas))
    cat=st.selectbox("Category",["All"]+categories); term=st.text_input("Search")
    for group,name,formula,notes in formulas:
        if (cat=="All" or cat==group) and term.lower() in (group+name+formula+notes).lower():
            with st.expander(f"{group} · {name}"):
                st.code(formula); st.write(notes)

elif page=="Performance & Notes":
    st.title("Performance & Study Notes")
    total,by=stats(); st.metric("Recorded attempts",total[0])
    if by:
        import pandas as pd
        data=[]
        for s in SUBJECTS:
            n,c=by.get(s["name"],(0,0))
            data.append({"Subject":s["name"],"Attempts":n,"Correct":c,"Accuracy (%)":round(c/n*100,1) if n else 0})
        st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
        st.bar_chart(pd.DataFrame(data).set_index("Subject")["Accuracy (%)"])
    else: st.info("Complete practice questions to build your performance history.")
    subj=st.selectbox("Subject for note",[s["name"] for s in SUBJECTS])
    note=st.text_area("Your note")
    if st.button("Save note",disabled=not note.strip()):
        c=db(); c.execute("INSERT INTO notes(subject,note,ts) VALUES(?,?,?)",(subj,note,datetime.now().isoformat())); c.commit(); c.close(); st.success("Note saved.")
    c=db(); notes=c.execute("SELECT subject,note,ts FROM notes ORDER BY id DESC LIMIT 50").fetchall(); c.close()
    for s,n,t in notes:
        with st.expander(f"{s} · {t[:10]}"): st.write(n)

elif page=="About":
    st.title("About CEM Prep")
    st.write("Independent study and practice application with original question bank, calculation utilities, formula references, and local progress tracking.")
    st.markdown("""
    - Not affiliated with or endorsed by AEE.
    - Questions are original practice items, not actual or recalled certification exam questions.
    - Some items are concept-reinforcement variants; use explanations and authoritative references to deepen understanding.
    - Confirm current exam format, content outline, eligibility, reference rules, and passing requirements with AEE.
    - Engineering calculators are educational aids, not a substitute for project-specific engineering review.
    """)
    st.write(f"**{len(QUESTIONS):,} questions** across **{len(SUBJECTS)} subject areas**.")

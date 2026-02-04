from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pandas as pd
import os
import math
from flask import session
from flask import jsonify, request
import os
import pandas as pd
from flask import send_file
import io


BASE_DIR = os.path.join(os.getcwd(), "data")
DATA_DIR = BASE_DIR  

app = Flask(__name__)

# ---------------- CONFIG ----------------

app.config['SECRET_KEY'] = 'eoffice_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# ---------------- DATABASE MODEL ----------------
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    department = db.Column(db.String(100), nullable=False)

    role = db.Column(db.String(20), default="user")  # admin / user

    username = db.Column(db.String(50), unique=True, nullable=False)

    email = db.Column(db.String(100), nullable=True)

    password = db.Column(db.String(200), nullable=False)


# ---------------- CREATE DB ----------------

with app.app_context():
    db.create_all()

#----------try---------------
# ================= DATA LOADER =================

# ================= DATA LOADER =================

def load_kpi_data():

    base_path = os.path.join(os.getcwd(), "data")

    # Read CSVs
    created_df = pd.read_csv(os.path.join(base_path, "filecreated.csv"))
    not_moved_df = pd.read_csv(os.path.join(base_path, "filecreatednotmoved.csv"))
    pending_df = pd.read_csv(os.path.join(base_path, "filepending.csv"))
    closed_df = pd.read_csv(os.path.join(base_path, "file_closed.csv"))
    active_df = pd.read_csv(os.path.join(base_path, "Total_Active_Users.csv"))


    # Convert numeric columns
    for df in [created_df, not_moved_df, pending_df, closed_df]:

        df['ElectronicFile'] = pd.to_numeric(df['ElectronicFile'], errors='coerce').fillna(0)
        df['PhysicalFile'] = pd.to_numeric(df['PhysicalFile'], errors='coerce').fillna(0)
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)


    # ---------------- CREATED ----------------

    created_total = int(created_df['Total'].sum())
    created_elec = int(created_df['ElectronicFile'].sum())
    created_phy = int(created_df['PhysicalFile'].sum())


    # ---------------- NOT MOVED ----------------

    not_moved_total = int(not_moved_df['Total'].sum())
    not_moved_elec = int(not_moved_df['ElectronicFile'].sum())
    not_moved_phy = int(not_moved_df['PhysicalFile'].sum())


    # ---------------- MOVED ----------------

    moved_total = created_total - not_moved_total
    moved_elec = created_elec - not_moved_elec
    moved_phy = created_phy - not_moved_phy


    # ---------------- PENDING ----------------

    pending_total = int(pending_df['Total'].sum())
    pending_elec = int(pending_df['ElectronicFile'].sum())
    pending_phy = int(pending_df['PhysicalFile'].sum())


    # ---------------- CLOSED ----------------

    closed_total = int(closed_df['Total'].sum())
    closed_elec = int(closed_df['ElectronicFile'].sum())
    closed_phy = int(closed_df['PhysicalFile'].sum())


    # ---------------- ACTIVE USERS ----------------
    active_df.columns = active_df.columns.str.strip()
    # Standardize active user calculation
    if "Active Users" in active_df.columns:
        active_users = int(active_df["Active Users"].sum())
    else:
        active_users = 0


    # ---------------- PERCENTAGES ----------------

    def calc_percent(part, total):
        if total == 0:
            return 0
        return round((part / total) * 100, 1)


    not_moved_percent = calc_percent(not_moved_total, created_total)
    pending_percent = calc_percent(pending_total, created_total)
    closed_percent = calc_percent(closed_total, created_total)


    # ---------------- RETURN ----------------

    return {

        "created": {
            "total": created_total,
            "electronic": created_elec,
            "physical": created_phy
        },

        "not_moved": {
    "total": not_moved_total,
    "electronic": not_moved_elec,
    "physical": not_moved_phy,
    "remaining": created_total - not_moved_total,
    "percent": not_moved_percent
},



        "moved": {
            "total": moved_total,
            "electronic": moved_elec,
            "physical": moved_phy
        },

        "pending": {
    "total": pending_total,
    "electronic": pending_elec,
    "physical": pending_phy,
    "remaining": created_total - pending_total,
    "percent": pending_percent
},



        "closed": {
    "total": closed_total,
    "electronic": closed_elec,
    "physical": closed_phy,
    "remaining": created_total - closed_total,
    "percent": closed_percent
},



        "active_users": active_users
    }

# ================= LOAD DEPARTMENTS =================

# ================= LOAD DEPARTMENTS =================

def load_departments():

    path = os.path.join(os.getcwd(), "data", "deptname_unique.csv")

    df = pd.read_csv(path)

    # If column name is DepartmentName
    if "DepartmentName" in df.columns:
        departments = df["DepartmentName"].dropna().tolist()
    else:
        # Take first column if name differs
        departments = df.iloc[:, 0].dropna().tolist()

    return sorted(departments)

def load_organizations():

    file_path = os.path.join("data", "filecreated.csv")

    df = pd.read_csv(file_path)

    # Get unique organization names
    orgs = df["OrgName"].dropna().unique().tolist()

    return sorted(orgs)


# ================= LOAD DETAIL TABLE =================

def load_detail_table():

    base = os.path.join(os.getcwd(), "data")

    # Load CSVs
    created = pd.read_csv(os.path.join(base, "filecreated.csv"))
    not_moved = pd.read_csv(os.path.join(base, "filecreatednotmoved.csv"))
    pending = pd.read_csv(os.path.join(base, "filepending.csv"))
    closed = pd.read_csv(os.path.join(base, "file_closed.csv"))


    # Select required columns
    cols = ["DepartmentName", "OrgName", "Total"]

    created = created[cols]
    not_moved = not_moved[cols]
    pending = pending[cols]
    closed = closed[cols]


    # Rename totals
    created = created.rename(columns={"Total": "created"})
    not_moved = not_moved.rename(columns={"Total": "not_moved"})
    pending = pending.rename(columns={"Total": "pending"})
    closed = closed.rename(columns={"Total": "closed"})


    # Group by Department + Org
    created = created.groupby(
        ["DepartmentName", "OrgName"], as_index=False
    ).sum()

    not_moved = not_moved.groupby(
        ["DepartmentName", "OrgName"], as_index=False
    ).sum()

    pending = pending.groupby(
        ["DepartmentName", "OrgName"], as_index=False
    ).sum()

    closed = closed.groupby(
        ["DepartmentName", "OrgName"], as_index=False
    ).sum()


    # Merge All
    df = created.merge(
        not_moved,
        on=["DepartmentName", "OrgName"],
        how="left"
    )

    df = df.merge(
        pending,
        on=["DepartmentName", "OrgName"],
        how="left"
    )

    df = df.merge(
        closed,
        on=["DepartmentName", "OrgName"],
        how="left"
    )


    # Fill NaN with 0
    df = df.fillna(0)


    # Convert to int
    for col in ["created", "not_moved", "pending", "closed"]:
        df[col] = df[col].astype(int)


    # ---------------- CALCULATIONS ----------------

    df["moved"] = df["created"] - df["not_moved"]


    def percent(a, b):
        if b == 0:
            return 0
        return round((a / b) * 100, 2)


    df["moved_pct"] = df.apply(
        lambda x: percent(x["moved"], x["created"]), axis=1
    )

    df["not_moved_pct"] = df.apply(
        lambda x: percent(x["not_moved"], x["created"]), axis=1
    )

    df["pending_pct"] = df.apply(
        lambda x: percent(x["pending"], x["created"]), axis=1
    )

    df["closed_pct"] = df.apply(
        lambda x: percent(x["closed"], x["created"]), axis=1
    )


    # ---------------- TOTAL ROW ----------------

    total = {

        "DepartmentName": "Total",
        "OrgName": "",

        "created": df["created"].sum(),
        "moved": df["moved"].sum(),
        "moved_pct": percent(
            df["moved"].sum(), df["created"].sum()
        ),

        "not_moved": df["not_moved"].sum(),
        "not_moved_pct": percent(
            df["not_moved"].sum(), df["created"].sum()
        ),

        "pending": df["pending"].sum(),
        "pending_pct": percent(
            df["pending"].sum(), df["created"].sum()
        ),

        "closed": df["closed"].sum(),
        "closed_pct": percent(
            df["closed"].sum(), df["created"].sum()
        ),
    }


    # Convert to list of dicts
    rows = df.to_dict(orient="records")

    rows.append(total)

    return rows

def get_last_refresh_time():

    path = os.path.join(DATA_DIR, "last_refresh.csv")

    try:
        df = pd.read_csv(path)

        if "last_refreshed" in df.columns:
            return df["last_refreshed"].iloc[0]

    except:
        pass

    return "Not Available"

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return redirect('/login')




# ---------- LOGIN ----------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):

            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['department'] = user.department
            

            return redirect('/dashboard')

        else:
            flash("Invalid Username or Password!", "danger")

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')


    role = session.get("role")
    user_dept = session.get("department")


    # ================= ADMIN =================
    if role == "admin":

        kpi_data = load_kpi_data()
        departments = load_departments()
        organizations = load_organizations()
        table_data = load_detail_table()


    # ================= NORMAL USER =================
    else:

        # Filter CSVs by department
        created = pd.read_csv(os.path.join(DATA_DIR,"filecreated.csv"))
        not_moved = pd.read_csv(os.path.join(DATA_DIR,"filecreatednotmoved.csv"))
        pending = pd.read_csv(os.path.join(DATA_DIR,"filepending.csv"))
        closed = pd.read_csv(os.path.join(DATA_DIR,"file_closed.csv"))
        users = pd.read_csv(os.path.join(DATA_DIR,"Total_Active_Users.csv"))


        created = created[created["DepartmentName"] == user_dept]
        not_moved = not_moved[not_moved["DepartmentName"] == user_dept]
        pending = pending[pending["DepartmentName"] == user_dept]
        closed = closed[closed["DepartmentName"] == user_dept]
        users = users[users["DepartmentName"] == user_dept]


        # ===== KPI =====

        def calc(df):
            ele = df["ElectronicFile"].sum()
            phy = df["PhysicalFile"].sum()
            return int(ele), int(phy), int(ele+phy)


        c_ele, c_phy, c_total = calc(created)
        nm_ele, nm_phy, nm_total = calc(not_moved)
        p_ele, p_phy, p_total = calc(pending)
        cl_ele, cl_phy, cl_total = calc(closed)


        m_ele = c_ele - nm_ele
        m_phy = c_phy - nm_phy
        m_total = c_total - nm_total


        base = c_total if c_total else 1


        def pct(a,b):
            return round((a/b)*100,1) if b else 0


        kpi_data = {

            "created":{
                "total":c_total,
                "electronic":c_ele,
                "physical":c_phy
            },

            "not_moved":{
                "total":nm_total,
                "electronic":nm_ele,
                "physical":nm_phy,
                "percent":pct(nm_total,base),
                "remaining":base-nm_total
            },

            "moved":{
                "total":m_total,
                "electronic":m_ele,
                "physical":m_phy
            },

            "pending":{
                "total":p_total,
                "electronic":p_ele,
                "physical":p_phy,
                "percent":pct(p_total,base),
                "remaining":base-p_total
            },

            "closed":{
                "total":cl_total,
                "electronic":cl_ele,
                "physical":cl_phy,
                "percent":pct(cl_total,base),
                "remaining":base-cl_total
            },

            "active_users": int(users["Active Users"].sum())
        }


        # ===== Filters =====
        departments = [user_dept]


        df_org = created.copy()
        organizations = sorted(
            df_org["OrgName"].dropna().unique().tolist()
        )


        # ===== Table =====
        table_data = load_detail_table()
        table_data = [

            r for r in table_data

            if r["DepartmentName"] == user_dept
            or r["DepartmentName"] == "Total"
        ]


    last_refresh = get_last_refresh_time()


    return render_template(

        'dashboard.html',

        data=kpi_data,
        departments=departments,
        organizations=organizations,
        table_data=table_data,
        last_refresh=last_refresh,

        user_role=role,
        user_dept=user_dept
    )



@app.route("/api/filter/department", methods=["POST"])
def filter_by_department():

    data = request.get_json()
    mode = data.get("mode", "total")

    if session.get("role") != "admin":
        departments = [ session.get("department") ]
    else:    
        departments = data.get("departments", [])

    # Load CSVs
    created = pd.read_csv(os.path.join(DATA_DIR,"filecreated.csv"))
    not_moved = pd.read_csv(os.path.join(DATA_DIR,"filecreatednotmoved.csv"))
    pending = pd.read_csv(os.path.join(DATA_DIR,"filepending.csv"))
    closed = pd.read_csv(os.path.join(DATA_DIR,"file_closed.csv"))

    # If department selected → filter
    if departments:

        created = created[created["DepartmentName"].isin(departments)]
        not_moved = not_moved[not_moved["DepartmentName"].isin(departments)]
        pending = pending[pending["DepartmentName"].isin(departments)]
        closed = closed[closed["DepartmentName"].isin(departments)]


    # Calculation function
    def calc(df):

        ele = df["ElectronicFile"].sum()
        phy = df["PhysicalFile"].sum()
        total = ele + phy


        if mode == "electronic":
            return int(ele), 0, int(ele)

        elif mode == "physical":
            return 0, int(phy), int(phy)

        else:
            return int(ele), int(phy), int(total)


    # Calculate all
    c_ele, c_phy, c_total = calc(created)
    nm_ele, nm_phy, nm_total = calc(not_moved)
    p_ele, p_phy, p_total = calc(pending)
    cl_ele, cl_phy, cl_total = calc(closed)


    # Moved = Created - Not Moved
    m_ele = c_ele - nm_ele
    m_phy = c_phy - nm_phy
    m_total = c_total - nm_total

    p_ele, p_phy, p_total = calc(pending)
    cl_ele, cl_phy, cl_total = calc(closed)

    # Total base (created)
    base = c_total if c_total != 0 else 1

    nm_pct = round((nm_total / base) * 100, 1)
    p_pct = round((p_total / base) * 100, 1)
    cl_pct = round((cl_total / base) * 100, 1)
    # ================= ACTIVE USERS =================

    users = pd.read_csv(os.path.join(DATA_DIR,"Total_Active_Users.csv"))

# Filter by department
    if departments:
        users = users[users["DepartmentName"].isin(departments)]

    active_users = int(users["Active Users"].sum())



    result = {

    "created": {
        "electronic": c_ele,
        "physical": c_phy,
        "total": c_total
    },

    "not_moved": {
        "electronic": nm_ele,
        "physical": nm_phy,
        "total": nm_total,
        "percent": nm_pct,
        "remaining": base - nm_total
    },

    "moved": {
        "electronic": m_ele,
        "physical": m_phy,
        "total": m_total
    },

    "pending": {
        "electronic": p_ele,
        "physical": p_phy,
        "total": p_total,
        "percent": p_pct,
        "remaining": base - p_total
    },

    "closed": {
        "electronic": cl_ele,
        "physical": cl_phy,
        "total": cl_total,
        "percent": cl_pct,
        "remaining": base - cl_total
    },

    "active_users": active_users



}



    return jsonify(result)

@app.route("/api/filter/table", methods=["POST"])
def filter_table():

    data = request.get_json()

    mode = data.get("mode", "total")   # total / electronic / physical


    if session.get("role") != "admin":
        departments = [session.get("department")]
    else:
        departments = data.get("departments", [])


    base = os.path.join(os.getcwd(), "data")


    # Load CSVs
    created = pd.read_csv(os.path.join(base, "filecreated.csv"))
    not_moved = pd.read_csv(os.path.join(base, "filecreatednotmoved.csv"))
    pending = pd.read_csv(os.path.join(base, "filepending.csv"))
    closed = pd.read_csv(os.path.join(base, "file_closed.csv"))


    # Filter departments
    if departments:

        created = created[created["DepartmentName"].isin(departments)]
        not_moved = not_moved[not_moved["DepartmentName"].isin(departments)]
        pending = pending[pending["DepartmentName"].isin(departments)]
        closed = closed[closed["DepartmentName"].isin(departments)]


    # ================= SELECT COLUMN BASED ON MODE =================

    if mode == "electronic":
        col = "ElectronicFile"

    elif mode == "physical":
        col = "PhysicalFile"

    else:
        col = "Total"


    # ================= SELECT COLUMNS =================

    cols = ["DepartmentName", "OrgName", col]


    created = created[cols].rename(columns={col: "created"})
    not_moved = not_moved[cols].rename(columns={col: "not_moved"})
    pending = pending[cols].rename(columns={col: "pending"})
    closed = closed[cols].rename(columns={col: "closed"})


    # ================= GROUP =================

    created = created.groupby(
        ["DepartmentName", "OrgName"], as_index=False
    ).sum()

    not_moved = not_moved.groupby(
        ["DepartmentName", "OrgName"], as_index=False
    ).sum()

    pending = pending.groupby(
        ["DepartmentName", "OrgName"], as_index=False
    ).sum()

    closed = closed.groupby(
        ["DepartmentName", "OrgName"], as_index=False
    ).sum()


    # ================= MERGE =================

    df = created.merge(not_moved, on=["DepartmentName","OrgName"], how="left")
    df = df.merge(pending, on=["DepartmentName","OrgName"], how="left")
    df = df.merge(closed, on=["DepartmentName","OrgName"], how="left")

    df = df.fillna(0)


    # ================= INT =================

    for c in ["created","not_moved","pending","closed"]:
        df[c] = df[c].astype(int)


    # ================= MOVED =================

    df["moved"] = df["created"] - df["not_moved"]


    # ================= PERCENT =================

    def pct(a,b):
        return round((a/b)*100,2) if b else 0


    df["moved_pct"] = df.apply(
        lambda x: pct(x["moved"], x["created"]), axis=1
    )

    df["not_moved_pct"] = df.apply(
        lambda x: pct(x["not_moved"], x["created"]), axis=1
    )

    df["pending_pct"] = df.apply(
        lambda x: pct(x["pending"], x["created"]), axis=1
    )

    df["closed_pct"] = df.apply(
        lambda x: pct(x["closed"], x["created"]), axis=1
    )


    # ================= TOTAL ROW =================

    total = {

        "DepartmentName":"Total",
        "OrgName":"",

        "created":int(df["created"].sum()),
        "moved":int(df["moved"].sum()),
        "moved_pct":pct(df["moved"].sum(),df["created"].sum()),

        "not_moved":int(df["not_moved"].sum()),
        "not_moved_pct":pct(df["not_moved"].sum(),df["created"].sum()),

        "pending":int(df["pending"].sum()),
        "pending_pct":pct(df["pending"].sum(),df["created"].sum()),

        "closed":int(df["closed"].sum()),
        "closed_pct":pct(df["closed"].sum(),df["created"].sum())
    }


    rows = df.to_dict(orient="records")
    rows.append(total)

    return jsonify(rows)


    data = request.get_json()
    if session.get("role") != "admin":
        departments = [ session.get("department") ]
    else:
        departments = data.get("departments", [])


    base = os.path.join(os.getcwd(), "data")

    # Load CSVs
    created = pd.read_csv(os.path.join(base, "filecreated.csv"))
    not_moved = pd.read_csv(os.path.join(base, "filecreatednotmoved.csv"))
    pending = pd.read_csv(os.path.join(base, "filepending.csv"))
    closed = pd.read_csv(os.path.join(base, "file_closed.csv"))


    # Filter
    if departments:

        created = created[created["DepartmentName"].isin(departments)]
        not_moved = not_moved[not_moved["DepartmentName"].isin(departments)]
        pending = pending[pending["DepartmentName"].isin(departments)]
        closed = closed[closed["DepartmentName"].isin(departments)]


    # Select columns
    cols = ["DepartmentName", "OrgName", "Total"]

    created = created[cols]
    not_moved = not_moved[cols]
    pending = pending[cols]
    closed = closed[cols]


    # Rename
    created = created.rename(columns={"Total": "created"})
    not_moved = not_moved.rename(columns={"Total": "not_moved"})
    pending = pending.rename(columns={"Total": "pending"})
    closed = closed.rename(columns={"Total": "closed"})


    # Group
    created = created.groupby(
        ["DepartmentName","OrgName"], as_index=False
    ).sum()

    not_moved = not_moved.groupby(
        ["DepartmentName","OrgName"], as_index=False
    ).sum()

    pending = pending.groupby(
        ["DepartmentName","OrgName"], as_index=False
    ).sum()

    closed = closed.groupby(
        ["DepartmentName","OrgName"], as_index=False
    ).sum()


    # Merge
    df = created.merge(
        not_moved,
        on=["DepartmentName","OrgName"],
        how="left"
    )

    df = df.merge(
        pending,
        on=["DepartmentName","OrgName"],
        how="left"
    )

    df = df.merge(
        closed,
        on=["DepartmentName","OrgName"],
        how="left"
    )


    df = df.fillna(0)


    # Int
    for c in ["created","not_moved","pending","closed"]:
        df[c] = df[c].astype(int)


    # Moved
    df["moved"] = df["created"] - df["not_moved"]


    # Percent
    def pct(a,b):
        return round((a/b)*100,2) if b else 0


    df["moved_pct"] = df.apply(
        lambda x: pct(x["moved"],x["created"]), axis=1
    )

    df["not_moved_pct"] = df.apply(
        lambda x: pct(x["not_moved"],x["created"]), axis=1
    )

    df["pending_pct"] = df.apply(
        lambda x: pct(x["pending"],x["created"]), axis=1
    )

    df["closed_pct"] = df.apply(
        lambda x: pct(x["closed"],x["created"]), axis=1
    )


    # Total row
    total = {

        "DepartmentName":"Total",
        "OrgName":"",

        "created":int(df["created"].sum()),
        "moved":int(df["moved"].sum()),
        "moved_pct":pct(df["moved"].sum(),df["created"].sum()),

        "not_moved":int(df["not_moved"].sum()),
        "not_moved_pct":pct(df["not_moved"].sum(),df["created"].sum()),

        "pending":int(df["pending"].sum()),
        "pending_pct":pct(df["pending"].sum(),df["created"].sum()),

        "closed":int(df["closed"].sum()),
        "closed_pct":pct(df["closed"].sum(),df["created"].sum())
    }


    rows = df.to_dict(orient="records")
    rows.append(total)

    return jsonify(rows)

@app.route("/api/filter/organization", methods=["POST"])
def filter_by_organization():
    data = request.get_json()
    org = data.get("organization")
    mode = data.get("mode", "total")
    
    

    if session.get("role") != "admin":

        df_check = pd.read_csv(os.path.join(DATA_DIR,"filecreated.csv"))

        allowed_orgs = df_check[
            df_check["DepartmentName"] == session.get("department")
        ]["OrgName"].unique().tolist()


        if org not in allowed_orgs:
            return jsonify({"error":"Unauthorized"}), 403

    # Load CSVs
    created = pd.read_csv(os.path.join(DATA_DIR,"filecreated.csv"))
    not_moved = pd.read_csv(os.path.join(DATA_DIR,"filecreatednotmoved.csv"))
    pending = pd.read_csv(os.path.join(DATA_DIR,"filepending.csv"))
    closed = pd.read_csv(os.path.join(DATA_DIR,"file_closed.csv"))
    users = pd.read_csv(os.path.join(DATA_DIR,"Total_Active_Users.csv"))


    # Filter by organization
    if org:

        created = created[created["OrgName"] == org]
        not_moved = not_moved[not_moved["OrgName"] == org]
        pending = pending[pending["OrgName"] == org]
        closed = closed[closed["OrgName"] == org]

        if "OrgName" in users.columns:
            users = users[users["OrgName"] == org]


    # Calculation helper
    def calc(df):

        ele = df["ElectronicFile"].sum()
        phy = df["PhysicalFile"].sum()
        total = ele + phy


        if mode == "electronic":
            return int(ele), 0, int(ele)

        elif mode == "physical":
            return 0, int(phy), int(phy)

        else:
            return int(ele), int(phy), int(total)



    # Calculate
    c_ele, c_phy, c_total = calc(created)
    nm_ele, nm_phy, nm_total = calc(not_moved)
    p_ele, p_phy, p_total = calc(pending)
    cl_ele, cl_phy, cl_total = calc(closed)


    # Moved
    m_ele = c_ele - nm_ele
    m_phy = c_phy - nm_phy
    m_total = c_total - nm_total


    base = c_total if c_total != 0 else 1


    # Percentages
    nm_pct = round((nm_total / base) * 100, 1)
    p_pct = round((p_total / base) * 100, 1)
    cl_pct = round((cl_total / base) * 100, 1)


    # Active users
    # Active users not applicable for organization filter
    active_users = "--"



    return jsonify({

        "created": {
            "electronic": c_ele,
            "physical": c_phy,
            "total": c_total
        },

        "not_moved": {
            "electronic": nm_ele,
            "physical": nm_phy,
            "total": nm_total,
            "percent": nm_pct,
            "remaining": base - nm_total
        },

        "moved": {
            "electronic": m_ele,
            "physical": m_phy,
            "total": m_total
        },

        "pending": {
            "electronic": p_ele,
            "physical": p_phy,
            "total": p_total,
            "percent": p_pct,
            "remaining": base - p_total
        },

        "closed": {
            "electronic": cl_ele,
            "physical": cl_phy,
            "total": cl_total,
            "percent": cl_pct,
            "remaining": base - cl_total
        },

        "active_users": active_users
    })

@app.route("/api/filter/table-by-org", methods=["POST"])
def filter_table_by_org():
    data = request.get_json()
    org = data.get("organization")
    mode = data.get("mode", "total")

    
    


    role = session.get("role")
    user_dept = session.get("department")


    base = os.path.join(os.getcwd(), "data")


    # Load CSVs
    created = pd.read_csv(os.path.join(base, "filecreated.csv"))
    not_moved = pd.read_csv(os.path.join(base, "filecreatednotmoved.csv"))
    pending = pd.read_csv(os.path.join(base, "filepending.csv"))
    closed = pd.read_csv(os.path.join(base, "file_closed.csv"))


    # ================= FILTER =================

    if role != "admin":

        # USER → dept + org
        created = created[
            (created["DepartmentName"] == user_dept) &
            (created["OrgName"] == org)
        ]

        not_moved = not_moved[
            (not_moved["DepartmentName"] == user_dept) &
            (not_moved["OrgName"] == org)
        ]

        pending = pending[
            (pending["DepartmentName"] == user_dept) &
            (pending["OrgName"] == org)
        ]

        closed = closed[
            (closed["DepartmentName"] == user_dept) &
            (closed["OrgName"] == org)
        ]


    else:

        # ADMIN → org only
        if org:

            created = created[created["OrgName"] == org]
            not_moved = not_moved[not_moved["OrgName"] == org]
            pending = pending[pending["OrgName"] == org]
            closed = closed[closed["OrgName"] == org]


    # ================= BUILD TABLE =================

    if mode == "electronic":
        col = "ElectronicFile"
    elif mode == "physical":
        col = "PhysicalFile"
    else:
        col = "Total"

    if mode == "electronic":
       col = "ElectronicFile"

    elif mode == "physical":
        col = "PhysicalFile"

    else:
        col = "Total"

    cols = ["DepartmentName", "OrgName", col]


    created = created[cols].rename(columns={col:"created"})
    not_moved = not_moved[cols].rename(columns={col:"not_moved"})
    pending = pending[cols].rename(columns={col:"pending"})
    closed = closed[cols].rename(columns={col:"closed"})


    created = created.groupby(["DepartmentName","OrgName"]).sum().reset_index()
    not_moved = not_moved.groupby(["DepartmentName","OrgName"]).sum().reset_index()
    pending = pending.groupby(["DepartmentName","OrgName"]).sum().reset_index()
    closed = closed.groupby(["DepartmentName","OrgName"]).sum().reset_index()


    df = created.merge(not_moved,on=["DepartmentName","OrgName"],how="left")
    df = df.merge(pending,on=["DepartmentName","OrgName"],how="left")
    df = df.merge(closed,on=["DepartmentName","OrgName"],how="left")

    df = df.fillna(0)


    # Int
    for c in ["created","not_moved","pending","closed"]:
        df[c] = df[c].astype(int)


    # Moved
    df["moved"] = df["created"] - df["not_moved"]


    # Percent
    def pct(a,b):
        return round((a/b)*100,2) if b else 0


    df["moved_pct"] = df.apply(
        lambda x: pct(x["moved"],x["created"]), axis=1
    )

    df["not_moved_pct"] = df.apply(
        lambda x: pct(x["not_moved"],x["created"]), axis=1
    )

    df["pending_pct"] = df.apply(
        lambda x: pct(x["pending"],x["created"]), axis=1
    )

    df["closed_pct"] = df.apply(
        lambda x: pct(x["closed"],x["created"]), axis=1
    )


    rows = df.to_dict(orient="records")

    return jsonify(rows)

@app.route("/api/filter/org-by-dept", methods=["POST"])
def org_by_department():

    data = request.get_json()

    departments = data.get("departments", [])


    role = session.get("role")
    user_dept = session.get("department")


    df = pd.read_csv(os.path.join(DATA_DIR, "filecreated.csv"))


    # ================= NORMAL USER =================
    if role != "admin":

        # Force only own department
        df = df[df["DepartmentName"] == user_dept]


    # ================= ADMIN =================
    else:

        if departments:
            df = df[df["DepartmentName"].isin(departments)]


    # Get unique orgs
    orgs = sorted(
        df["OrgName"]
        .dropna()
        .unique()
        .tolist()
    )


    return jsonify(orgs)

@app.route("/api/download/table", methods=["POST"])
def download_table_excel():

    data = request.get_json()

    rows = data.get("rows", [])

    if not rows:
        return jsonify({"error":"No data"}), 400


    # Convert rows to DataFrame
    df = pd.DataFrame(rows)


    # Rename columns (remove % sign)
    df = df.rename(columns={

        "DepartmentName":"Department",
        "OrgName":"Organization",

        "created":"Files Created",
        "moved":"Total Moved",
        "moved_pct":"Moved %",

        "not_moved":"Files Not Moved",
        "not_moved_pct":"Not Moved %",

        "pending":"Files Pending",
        "pending_pct":"Pending %",

        "closed":"Files Closed",
        "closed_pct":"Closed %"
    })


    # Create Excel in memory
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dashboard")


    output.seek(0)


    return send_file(

        output,

        as_attachment=True,

        download_name="dashboard_table.xlsx",

        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
  

@app.route("/signup")
def block_signup():
    return redirect("/login")

# ---------- LOGOUT ----------

@app.route('/logout')
def logout():

    session.clear()
    return redirect('/login')


# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask,redirect,url_for,render_template,request,flash
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import json
import sqlite3

app = Flask(__name__)
app.secret_key = 'abcd123'

@app.route('/')
@app.route('/index')
def hello_world():
    return render_template('index.html')

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        connect = sqlite3.connect('database.db')
        connect.execute('CREATE TABLE IF NOT EXISTS User (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT NOT NULL,email TEXT NOT NULL,password TEXT NOT NULL)')
        cursor.execute('''
            INSERT INTO User (username, email, password) VALUES (?, ?, ?)
        ''', ('admin', 'admin@example.com', '1234'))
        conn.commit()
        

#init_db()

# @app.route('/home/<int:score>')
# def home(score):
#     return '<h1>Home Page</h1><br> marks scored:  '+ str(score)
@app.route('/login')
def login():
    return render_template('login.html') 

@app.route('/home',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM User WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            
            if user:
                return redirect(url_for('worldCup'))
            else:
                flash('Incorrect username or password.', 'danger')
        # if username == "admin" and password == "1234":
        #     return redirect(url_for('match_res'))
        # else:
        #     flash('Incorrect username or password.', 'danger')
    return render_template('login.html')

@app.route('/worldCup')
def worldCup():
    return render_template('worldCup2022.html')

@app.route('/results/<int:score>')
def results(score):
    result=""
    if score<50:
        result = 'fail'
    else:
        result = 'home'
    #return result
    return redirect(url_for(result,score=score))

@app.route('/studVsmarks')
def studVsmarks():

    marks = [12,34,32,48,45]
    stud = ['Juhi','Nistha','Hinal','Zeel','Sakshi']
    plt.plot(marks)
    x=plt.show()
    return x 
#Batting Summary   
df_batting = pd.read_csv("E:\\BSc.IT\\TY\\DS Project\\data\\batting_summary.csv")
df_batting['boundary_runs'] = df_batting['fours']*4 + df_batting['sixes']*6
Total_Runs = df_batting.groupby(['batsmanName']).agg({'runs': 'sum', 'out': 'sum', 'balls': 'sum', 'boundary_runs': 'sum','battingPos':'sum','match_id':'count'})
Total_Runs['Batting_Avg'] =  np.divide(Total_Runs['runs'],Total_Runs['out']).replace([np.inf,-np.inf],0).round(2)
Total_Runs['Strike_Rate'] = ((Total_Runs['runs'] / Total_Runs['balls']).fillna(0) * 100).round(2)
Total_Runs['avg_battingPos'] = np.int64(np.ceil(Total_Runs['battingPos']/Total_Runs['match_id']) )
Total_Runs['boundaryPerc'] = (Total_Runs['boundary_runs']/Total_Runs['runs']*100).round(2)
Total_Runs['avg_balls_faced'] = np.ceil(Total_Runs['balls']/Total_Runs['match_id'])
Total_Runs.reset_index(inplace=True)
Total_Runs.rename({'match_id':'inningsBatted','batsmanName': 'playerName'},axis=1,inplace=True)
#Players
df_players = pd.read_csv("E:\\BSc.IT\\TY\\DS Project\\data\\dim_players.csv")
df_players['name'] = df_players['name'].apply(lambda x: x.replace('(c)', ''))
df_players.rename({'name':'playerName'},axis=1,inplace=True)
#Bowling
def bowling():
    df_bowling = pd.read_csv('E:\\BSc.IT\\TY\\DS Project\\data\\bowling_summary.csv')
    df_bowling['balls'] = df_bowling['overs1']*6 + df_bowling['overs2']
    bowlers = df_bowling.groupby(['bowlerName']).agg({'wickets': 'sum', 'balls': 'sum', 'runs': 'sum','match_id':'count','zeros':'sum'})
    bowlers.reset_index(inplace=True)
    bowlers.rename({'match_id':'inningsBowled','balls':'ballsBowled','runs':'Runs_conceded','bowlerName':'playerName'},axis=1,inplace=True)
    bowlers['Economy'] = np.divide(bowlers['Runs_conceded'],bowlers['ballsBowled']/6).replace([np.inf, -np.inf], 0).round(2)
    bowlers['Bowling_Strike_Rate'] = np.divide(bowlers['ballsBowled'],bowlers['wickets']).replace([np.inf, -np.inf],0).round(2)
    bowlers['Bowling_Avg'] = (np.divide(bowlers['Runs_conceded'],bowlers['wickets']).replace([np.inf, -np.inf],0)).round(2)
    bowlers['Dot_Ball'] = (((bowlers['zeros']/bowlers['ballsBowled'])*100).replace([np.inf,-np.inf],0)).round(2)
    return bowlers


@app.route('/match_res')
def match_res():
    openers = Total_Runs.loc[(Total_Runs['Batting_Avg']>30) & (Total_Runs['Strike_Rate']>140) & (Total_Runs['inningsBatted']>3) & (Total_Runs['boundaryPerc']>50.00) & (Total_Runs['avg_battingPos']<4),['playerName','Strike_Rate','balls','inningsBatted','Batting_Avg','avg_battingPos','boundaryPerc','runs']]
    df = pd.merge(openers,df_players,on='playerName',how='left')
    df_openers = df.loc[:,['playerName','team','battingStyle','inningsBatted','runs','balls','Strike_Rate','Batting_Avg','avg_battingPos','boundaryPerc']]
    df_openers_list = df_openers.to_dict(orient='records')
    cols = df_openers.columns.to_list()
    # ['Batsman Name',
    #             'Team',
    #             'Batting Style',
    #             'Innings Batted',
    #             'Runs',
    #             'Average Balls Faced',
    #             'Strike Rate',
    #             'Batting Average',
    #             'Average Batting Position',
    #             'Boundary Percentage']
    return render_template('match_res.html',cols=cols,openers=df_openers_list,pCat="Power Hitters / Openers",plotLink=url_for('static', filename='plots/openers(Strike Rate vs Batting Average).png'),timePlot=url_for('static', filename='plots/Batting Average Over Time.png'),timePlot2=url_for('static', filename='plots/Strike Rate Over Time.png'),detLink="visOpeners")

@app.route('/anchors')
def anchors():
    anchors = Total_Runs.loc[(Total_Runs['Batting_Avg']>40) & (Total_Runs['Strike_Rate']>125) & (Total_Runs['inningsBatted']>3) & (Total_Runs['avg_balls_faced']>20) & (Total_Runs['avg_battingPos']>2)]
    df = pd.merge(anchors,df_players,on='playerName',how='left')
    df_anchors = df.loc[:,['playerName','team','battingStyle','bowlingStyle','inningsBatted','runs','balls','Strike_Rate','Batting_Avg','avg_battingPos','boundaryPerc']]
    df_anchors_list = df_anchors.sort_values(by='runs',ascending=False).to_dict(orient='records')
    cols = df_anchors.columns.tolist()
    # ['Batsman Name',
    #             'Team',
    #             'Batting Style',
    #             'Innings Batted',
    #             'Runs',
    #             'Average Balls Faced',
    #             'Strike Rate',
    #             'Batting Average',
    #             'Average Batting Position',
    #             'Boundary Percentage']
    return render_template('match_res.html',cols = cols,openers=df_anchors_list,pCat="Anchors/MIDDLE ORDER",plotLink=url_for('static',filename='plots/anchors(Strike Rate vs Batting Average).png'),timePlot=url_for('static', filename='plots/Batting Average Over Time.png'),timePlot2=url_for('static', filename='plots/Strike Rate Over Time.png'),detLink="visAnchors")

@app.route('/finishers')
def finishers():
    bowlers = bowling()
    merged_df = pd.merge(Total_Runs,bowlers,on='playerName')
    df = merged_df.loc[(merged_df['Batting_Avg']>25) & (merged_df['Strike_Rate']>130) & (merged_df['inningsBatted']>3) & (merged_df['inningsBowled']>1) & (merged_df['avg_battingPos']>4) & (merged_df['avg_balls_faced']>12)]
    df_finishers = pd.merge(df,df_players,on='playerName',how='left')
    finishers = df_finishers.loc[:,['playerName','team','battingStyle','bowlingStyle','inningsBatted','runs','avg_balls_faced','Batting_Avg','Strike_Rate','inningsBowled','wickets','Economy','Bowling_Strike_Rate']]
    finishers_list = finishers.sort_values(by='Strike_Rate',ascending=False).to_dict(orient='records')
    cols = finishers.columns.to_list()
                # ['Name',
                # 'Team',
                # 'Batting Style',
                # 'Innings Batted',
                # 'Runs',
                # 'Average Balls Faced',
                # 'Strike Rate',
                # 'Batting Average',
                # 'Average Batting Position','Boundary Percentage','Bowling Style',
                # 'inningsBowled','wickets','Economy','Bowling_Strike_Rate',]
    return render_template('match_res.html',cols = cols,openers=finishers_list,pCat="Finisher/Lower Order Anchor",plotLink=url_for('static',filename='plots/finishers(Strike Rate vs Batting Average).png'),timePlot=url_for('static', filename='plots/Batting Average Over Time.png'),timePlot2=url_for('static', filename='plots/Strike Rate Over Time.png'),detLink = "visFinishers")

@app.route('/allRounders')
def allRounders():
    bowlers = bowling()
    merged_df = pd.merge(Total_Runs,bowlers,on='playerName')
    df = merged_df.loc[(merged_df['Batting_Avg']>15) & (merged_df['Strike_Rate']>140) & (merged_df['inningsBatted']>2) & (merged_df['avg_battingPos']>4) & (merged_df['inningsBowled']>2) & (merged_df['Economy']<7) & (merged_df['Bowling_Strike_Rate']<20)]
    df_allRounders = pd.merge(df,df_players,on='playerName',how='left')
    allRounders = df_allRounders.loc[:,['playerName','team','battingStyle','bowlingStyle','inningsBatted','runs','Batting_Avg','Strike_Rate','inningsBowled','ballsBowled','wickets','Economy','Bowling_Strike_Rate']]
    allRounders_list = allRounders.sort_values(by='Strike_Rate',ascending=False).to_dict(orient='records')
    cols = allRounders.columns.tolist()
    #['Batsman Name',
    #             'Team',
    #             'Batting Style',
    #             'Innings Batted',
    #             'Runs',
    #             'Average Balls Faced',
    #             'Strike Rate',
    #             'Batting Average',
    #             'Average Batting Position',
    #             'Boundary Percentage']
    return render_template('match_res.html',cols = cols,openers=allRounders_list,pCat="All Rounders",plotLink=url_for('static',filename='plots/finishers(Economy vs Bowling Strike Rate).png'),timePlot=url_for('static', filename='plots/Batting Average Over Time.png'),timePlot2=url_for('static', filename='plots/Strike Rate Over Time.png'),detLink = "visAllRounders")

@app.route('/fastX')
def fastX():
    bowlers = bowling()
    fast_players = pd.merge(bowlers,df_players,on='playerName')
    f_bowlers = fast_players.loc[
    (fast_players['Dot_Ball'] > 40) &
    (fast_players['Economy'] < 7) &
    (fast_players['Bowling_Strike_Rate'] < 16) &
    (fast_players['inningsBowled']>4) &
    (fast_players['Bowling_Avg'] < 20) &
    (fast_players['bowlingStyle'].str.contains("fast",case=False,na  =False))]
    df_fast = f_bowlers.loc[:,['playerName','team','bowlingStyle','inningsBowled','ballsBowled','Runs_conceded','wickets','Economy','Bowling_Avg','Bowling_Strike_Rate','Dot_Ball']] 
    cols = df_fast.columns.to_list()  
    # ['Batsman Name',
    #             'Team',
    #             'Batting Style',
    #             'Bowling Style',
    #             'Innings Bowled',
    #             'Balls bowled'
    #             'Runs Concceded','wickets','Economy','Bowling_avergae','Bowling_Strike_Rate',
    #             ]
    return render_template('match_res.html',cols=cols,openers=df_fast.sort_values(by='wickets',ascending=False).to_dict(orient='records'),pCat="Specialist Fast Bowlers",plotLink=url_for('static',filename='plots/fast(Economy vs Bowling Strike Rate).png'),timePlot=url_for('static', filename='plots/Batting Average Over Time.png'),timePlot2=url_for('static', filename='plots/Strike Rate Over Time.png'),detLink = 'visFast')
    

@app.route('/visOpeners')
def visOpeners():
    return render_template('visOpeners.html')

@app.route('/visAnchors')
def visAnchors():
    return render_template('visAnchors.html')

@app.route('/visFinishers')
def visFinishers():
    return render_template('visFinishers.html')

@app.route('/visAllRounders')
def visAllRounders():
    return render_template('visAllRounders.html')

@app.route('/visFast')
def visFast():
    return render_template('visFast.html')

if __name__ == '__main__':
    app.run(debug=True)

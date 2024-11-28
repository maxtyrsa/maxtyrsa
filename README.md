<h1 align="center">Hi there, I'm <a href="https://daniilshat.ru/" target="_blank">Max</a> 
<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/></h1>

[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=i+am+a+Data+Analyst)](https://git.io/typing-svg)

<div id="header" align="center">
  <img src="https://s10.gifyu.com/images/SYolE.gif" width="400"/>
</div>

<hr width="100%" color="green" />

<h3>About me:</h3>

An ambitious graduate of karpov.courses with experience in content management and logistics, aspiring to start a career as a junior data analyst. 
I have skills in Python programming, working with SQL, Git, Linux, BI tools and Excel. 
My qualities include initiative, quick learning, and a commitment to continuous development.

<hr width="100%" color="green" />

- Python programming using NumPy, Pandas, MatPlotLib, Seaborn libraries.
- Skills in writing SQL queries for the PostgreSQL database, including group by, distinct, join, where, having, union and window functions.
- Experience working in Linux, writing bash scripts for personal projects.
- Strong command of Git (push/pull, pull request, merge) and work with remote repositories on GitHub.
- The use of Metabase and Superset BI tools for data visualization.
- Excel skills.

I currently work in an online store, «Kupi-Flakon»

Email: tyrsa@doctor.com

<hr width="100%" color="green" />


| Rank | Languages     | Level
|-----:|---------------|-------|
|     1| English       | A2    |
|     2| German        | A2    |

<hr width="100%" color="green" />

<h3>Portfolio:</h3>

| Project № | Name and link     | Task  |
|--------:| ------------------|-------|
|  1  | Average Profit Margin           | Период анализа - с 1.04.23 по 10.04.23 . В анализе должны участвовать только продажи изделий с общей суммой и себестоимостью больше 0 рублей . В ответе необходимо получить два значения наценки - среднюю наценку на ювелирные изделия из золота и среднюю наценку на ювелирные изделия из серебра. Сгруппировать изделия по металлу нужно на основе поля "Товарная группа". Товарная группа изделий из серебра начинается на "СИ", все остальные изделия - это золото.    |


![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Vim](https://img.shields.io/badge/VIM-%2311AB00.svg?style=for-the-badge&logo=vim&logoColor=white)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![LibreOffice](https://img.shields.io/badge/LibreOffice-%2318A303?style=for-the-badge&logo=LibreOffice&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Kali](https://img.shields.io/badge/Kali-268BEE?style=for-the-badge&logo=kalilinux&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)


# You'll need to install PyJWT via pip 'pip install PyJWT' or your project packages file

import jwt
import time

METABASE_SITE_URL = "http://localhost:3000"
METABASE_SECRET_KEY = "72df9fe65a6e203ba1a3b80aafcd55dcbdc125040a8df2c3d8442fdabda60b49"

payload = {
  "resource": {"question": 28},
  "params": {
    
  },
  "exp": round(time.time()) + (60 * 10) # 10 minute expiration
}
token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

iframeUrl = METABASE_SITE_URL + "/embed/question/" + token +
  "#bordered=true&titled=true"

# Chappy-Crawler
2023 산학 심화 R&amp;D 프로젝트: **문제 및 학생 데이터 수집**

## Dataset

**수집된 데이터는 private repo 에 따로 저장**

### Amount of data

`Codechef`
|project.csv|problem.csv|code.csv|
|:---:|:---:|:---:|
|4265|TBD|TBD|
|132KB|TBD|TBD|

`Codeforces`
|contest.csv|problem.csv|code.csv|
|:---:|:---:|:---:|
|10515|TBD|TBD|
|321KB|TBD|TBD|

### Data structure
#### Codechef

`project.csv`
|projectID|datatime|
|:---:|:---:|
|START01|2023-07-10 11:10:26 AM|
|GDTURN|2023-07-10 11:10:26 AM|

`problem.csv`
|projectID|title|problem|tags|input_tc|output_tc|datatime|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|START01|Number Mirror|"Write a program that takes a number N as the input, and prints it to the output."|"['Implementation', 'Algorithms']"|123|123|2023-07-10 08:45:54 PM|
|GDTURN|Good Turn|"Chef and Chefina are playing with dice. In one turn, both of them roll their dice at once. They consider a turn to be good if the sum of the numbers on their dice is greater than 6. Given that in a particular turn Chef and Chefina got X and Y on their respective dice, find whether the turn was good."|"['Conditional Statements', 'Basic Programming Concepts']"|"4 1 4 3 4 4 2 2 6"|"NO YES NO YES"|2023-07-10 08:46:03 PM|

`code.csv`
|projectID|submissionID|username|status|language|extension|code|datatime|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|START01|100094959|robiulislamiuj|error|Python3|.py|"#include<stdio.h> int main() {int t; scanf(""%d"",&t); while(t--){   int a;   scanf(""%d"",&a);    printf(""%d\n"",a);  }}"|2023-07-10 09:25:59 PM|
|START01|100094894|sanjaymanda31|correct|Python3|.py|"# cook your dish here n=int(input()) print(n)"|2023-07-10 09:26:05 PM|

#### Codeforces

`contest.csv`
|contestID|problemID|datatime|
|:---:|:---:|:---:|
|1846|A|2023-07-10 11:20:03 PM|
|1846|B|2023-07-10 11:20:03 PM|

`problem.csv`
|contestID|problemID|title|problem|tags|input_tc|output_tc|datatime|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|1846|A|A. Rudolph and Cut the Rope|"There are 𝑛 nails driven into the wall, the 𝑖 -th nail is driven 𝑎 𝑖 meters above the ground, one end of the 𝑏 𝑖 meters long rope is tied to it. All nails hang at different heights one above the other. One candy is tied to all ropes at once. Candy is tied to end of a rope that is not tied to a nail.To take the candy, you need to lower it to the ground. To do this, Rudolph can cut some ropes, one at a time  Help Rudolph find the minimum number of ropes that must be cut to get the candy.The figure shows an example of the first test:"|"['implementation', 'math']"|"4 3 4 3 3 1 1 2 4 9 2 5 2 7 7 3 4 5 11 7 5 10 12 9 3 2 1 5 3 5 6 4 5 7 7"|"2 2 3 0"|2023-07-11 09:46:56 AM|

`code.csv`
|contestID|problemID|submissionID|username|status|language|extension|code|datatime|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|1846|A|213149889|br0kenb4ain|error|Python 2|.py|"for _ in range(int(input())): n = int(input()) ans = 0 for i in range(n):  a, b = map(int, input().split());  if (a > b):   ans+=1 print(ans)"|2023-07-11 10:40:50 AM|

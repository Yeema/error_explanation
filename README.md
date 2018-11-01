# error_explanation
## usage: 
1. python explain.py
2. 利用 cal_explain（original, correction）得到結果
3. correction format 為testcase所示
## test case:
1. case1
  * original : We discussed about the issue .
  * correction : We discussed [-about-] the issue .
2. case2
  * original : The train arrived at exactly twelve past three .
  * correction : The train arrived at exactly twelve {+minutes+} past three.
3. case3
  * original : I am a honest teacher.","I am [-a-] {+an+} honest teacher.
  * correction : School finishes at five in morning .","School finishes at five in {+the+} morning .
4. case4
  * School finishes at five in morning .
  * School finishes at five in {+the+} morning .


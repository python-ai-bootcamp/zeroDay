stdin_mock='''his name was robert paulson
2432902008176640000
        *
       ***
      *****
     *******
    *********
   *********** 
  *************
 ***************
 '''
 # takes from runtime argument the script it should execute
 # it then proceeds to execute the script
 # then it validates its STDOU (and also collects STDERR in case script crashed)
 # returns the following output to STDOUT
 # PASS/FAIL
 # if fails, returns a reason (stacktrace or other which will be the rest of the stdout)
 # PASS/FAIL will be saved in assignment_data.json for that assignment's submission as the "result" key's value
 # rest of the stdout lines will be saved in assignment_Data.json for that assignment's submission as the FAIL_message key's value
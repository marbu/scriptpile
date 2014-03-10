#!/bin/bash
# example of variable dereferencing in bash (known as 'indirect expansion')

check_var()                                                     
{                                                                               
  local ENV_VAR=$1                                                              
  if [[ -v ${ENV_VAR} ]]; then                                                  
    echo "pass variable $ENV_VAR is set"                                      
  else                                                                          
    echo "fail variable $ENV_VAR is undefined"                                
  fi                                                                            
  if [[ -d ${!ENV_VAR} ]]; then                                                 
    echo "pass variable $ENV_VAR points to existing directory"                
  else                                                                          
    echo "fail variable $ENV_VAR points to directory which doesn't exist"     
  fi                                                                            
} 

TMP_HOME=/home/martin/tmp
FOO_HOME=/home/martin/foo
unset NOO_HONE

for ENV_VAR in {TMP,FOO,NOO}_HOME; do
  check_var $ENV_VAR
done

#! /bin/bash

location=asia-northeast1
dev=sandbox-terunrun-dev
stg=sandbox-terunrun-stg
prd=sandbox-terunrun-prd

init() {
  STARTTIME=`date +%Y%m%d_%H%M%S`
  echo $STARTTIME > import_dags.log
}

import_dags() {
  echo start importing dags to $1 >>  import_dags.log
  echo imported dags----- >> import_dags.log
  while read line
  do
    i=$((i+1))
      echo importing ${line} to $1 ...
      gcloud composer environments storage dags import --project $1 --environment $1 --location $location --source ../src/dags/${line}
      wait
      echo ${line} >> import_dags.log
  done < import_dag_list.txt
  echo imported dags----- >> import_dags.log
  echo number of imported dags is ${i} >> import_dags.log
  echo end importing dags to $1 >> import_dags.log
}

import_sqls() {
  echo start importing sqls to $bucket >>  import_dags.log
  echo imported sqls----- >> import_dags.log
  while read line
  do
    i=$((i+1))
      echo importing ${line} to $1 ...
      gcloud composer environments storage dags import --project $1 --environment $1 --location $location --source ../src/dags/sql/${line} --destination /sql
      wait
      echo ${line} >> import_dags.log
  done < import_sql_list.txt
  echo imported sqls----- >> import_dags.log
  echo number of imported sqls is ${j} >> import_dags.log
  echo end importing sqls to $bucket >> import_dags.log
}

import_data() {
  echo start importing data to $bucket >>  import_dags.log
  echo imported data----- >> import_dags.log
  while read line
  do
    i=$((i+1))
      echo importing ${line} to $1 ...
      gcloud composer environments storage data import --project $1 --environment $1 --location $location --source ../data/${line}
      wait
      echo ${line} >> import_dags.log
  done < import_data_list.txt
  echo imported data----- >> import_dags.log
  echo number of imported data is ${j} >> import_dags.log
  echo end importing data to $bucket >> import_dags.log
}

terminate() {
  ENDTIME=`date +%Y%m%d_%H%M%S`
  echo $ENDTIME >> import_dags.log
}

import() {
  read -p "Select you want to import

composer environment name: $1

0) all
1) dags
2) dags/sql
3) data

  : " type
  case $type in
    "0")
      import_dags $1
      import_sqls $1
      import_data $1
    ;;
    "1")
      import_dags $1
    ;;
    "2")
      import_sqls $1
    ;;
    "3")
      import_data $1
    ;;
    *)
      echo "$type is not supported"
      exit 1
    ;;
  esac
}

read -p "Select composer environment name by number
1) $dev
2) $int
3) $prd
: " project

init

i=0
j=0

case $project in
  "1")
    import $dev
  ;;
  "2")
    import $int
  ;;
  "3")
    import $prd
  ;;
  *)
    echo "$project is not supported"
    exit 1
  ;;
esac

terminate

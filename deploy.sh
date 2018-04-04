#!/usr/bin/env bash
pip install -t vendors -r requirements.txt
ENV=preproduction

if [ -n "$1" ];
then
    ENV=$1
fi

if [ -z "$2" ];
then
    echo "No AWS Profile set using default"
    sls deploy --stage $ENV --verbose
else
    echo "Using given AWS Profile"
    echo $2
    sls deploy --stage $ENV --verbose --aws-profile $2
fi

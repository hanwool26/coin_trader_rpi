#!/bin/bash
# usage : ./profit_sum.sh /usr/bin/coin_trade/output/report_file.txt

report_folder="/usr/share/coin_trade/output"
total_sum=0.0

function usage
{
    echo "[usage] ./profit_sum.sh -[option] -[file]"
    echo "[option]"
    echo "m - montly profit"
    echo "    ./profit_sum.sh -m /usr/share/coin_trade/output/report_xxxx-xx.txt"
    echo "a - total profit"
    echo "    ./profit_sum.sh -a"
}

while getopts "m:a" opt; do
    case ${opt} in    
        m)
            report_title=$(basename $OPTARG)
            echo "montly profit"
            echo "-------------------------"
            echo ${report_title%.*}
            sum=$(echo $(awk -F'손익 : ' '{sum+=$2} END {print sum}' $OPTARG | awk -F'원' '{print $1}' | awk '{sum+=$1} END {print sum}'))
            echo "총 손익 : $sum원" 
            ;;
        a)
            echo "total profit"
            while read report_file; do
            echo "-------------------------"
            sum=$(echo $(awk -F'손익 : ' '{sum+=$2} END {print sum}' $report_folder/$report_file | awk -F'원' '{print $1}' | awk '{sum+=$1} END {print sum}'))
            echo ${report_file%.*}
            echo "손익 : $sum원" 
            total_sum=$(echo "$total_sum + $sum" | bc -l)
            done < <(ls $report_folder)
            echo "-------------------------"
            echo "총 손익 : $total_sum원"
            ;;
        \?)
            usage
            ;;
    esac
done

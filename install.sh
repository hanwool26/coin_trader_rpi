#!/bin/bash

if [ "$EUID" -ne 0 ]
then
	echo "Please run as root"
	exit
fi

BASEDIR=$(dirname $0)
WORK_DIRECTORY="/usr/share/coin_trade/"

if [ ! -d "$WORK_DIRECTORY" ]; then
  echo "create work directory..."
  mkdir -p /usr/share/coin_trade/res
  mkdir -p /usr/share/coin_trade/output
  chmod -R 777 /usr/share/coin_trade
fi

echo "copy scripts..."
systemctl stop coin_trade.service
rm -rf /usr/local/bin/coin_trade_service
cp -r ../coin_trader_rpi /usr/local/bin/coin_trade_service
cp tool/systemd/coin_trade.sh /usr/bin/
cp tool/systemd/coin_trade.service /lib/systemd/system/coin_trade.service
systemctl enable coin_trade.service
systemctl restart coin_trade.service

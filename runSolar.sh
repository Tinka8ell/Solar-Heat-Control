#
rm /temp/solar9.txt
mv /temp/solar8.txt /temp/solar9.txt
mv /temp/solar7.txt /temp/solar8.txt
mv /temp/solar6.txt /temp/solar7.txt
mv /temp/solar5.txt /temp/solar6.txt
mv /temp/solar4.txt /temp/solar5.txt
mv /temp/solar3.txt /temp/solar4.txt
mv /temp/solar2.txt /temp/solar3.txt
mv /temp/solar1.txt /temp/solar2.txt
mv /temp/solar.txt /temp/solar1.txt
rm /temp/solar9.err
mv /temp/solar8.err /temp/solar9.err
mv /temp/solar7.err /temp/solar8.err
mv /temp/solar6.err /temp/solar7.err
mv /temp/solar5.err /temp/solar6.err
mv /temp/solar4.err /temp/solar5.err
mv /temp/solar3.err /temp/solar4.err
mv /temp/solar2.err /temp/solar3.err
mv /temp/solar1.err /temp/solar2.err
mv /temp/solar.err /temp/solar1.err
cd /home/pi/solar
python3 /home/pi/solar/Controller.py 2> /temp/solar.err > /temp/solar.txt

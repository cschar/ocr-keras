#Dev Notes

for configuring the custom search engine: 
https://cse.google.com/cse/all

conda envs
https://conda.io/docs/py2or3.html

pip install -r requirements.txt
conda install --file conda-requirements.txt

bug when doing uwsgi --ini ocr.ini

uwsgi: error while loading shared libraries: libpcre.so.1: cannot open shared object file: No such file or directory

solution: (would only work with sudo, not current user)
sudo find / -name libpcre.so.1
#delete one root had installed (not needed)
#set to the user installed path
export LD_LIBRARY_PATH=<the_path>:$LD_LIBRARY_PATH


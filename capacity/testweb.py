from urllib.request import urlopen
from string import Template
import re
import pickle

link = Template('http://www.codetables.de/BKLC/Tables.php?q=${q}&n0=1&n1=${end1}&k0=1&k1=${end2}')

q_list = [2, 3, 4, 5, 7, 8, 9, 11, 13, 15, 16]

valid_q2end = {2: 256, 3: 243, 4: 256, 5: 130, 7: 100, 8: 130, 9: 130,
        11: 130, 13: 130, 15: 257, 16: 130}

database = {}

def get_valid_params():
    q2end = {}
    for cur_q in q_list:
        big_end = 257
        for end in range(big_end, 49, -1):
            request_link = link.substitute(q=cur_q, end1=end, end2=end)
            # print(request_link)
            myURL = urlopen(link.substitute(q=cur_q, end1=end, end2=end))
            content = myURL.read().decode('utf-8')
            if "bad range for the length" not in content:
                big_end = end
                break
        q2end[cur_q] = big_end
        print(cur_q, big_end)
    print(q2end)

def get_content(cur_q):
    end = valid_q2end[cur_q]
    myURL = urlopen(link.substitute(q=cur_q, end1=end, end2=end))
    content = myURL.read().decode('utf-8')
    assert  "bad range for the length" not in content
    return content

def extract_tables(content):
    # content = 'HREF="BKLC.php?q=2&n=21&k=14">4</A>'
    # HREF="BKLC.php?q=2&n=21&k=14">4</A>
    result = re.findall('HREF="BKLC.php\?q=(\d+)&n=(\d+)&k=(\d+)">([0-9|\-]{1,20})</A>', content)
    # print(result)
    for res in result:
    # print(matchObj)
        q, n, k, answer = res
        if "-" in answer:
            lower, upper = map(int, answer.split("-"))
            assert lower < upper
            answer = lower
        q, n, k, answer = map(int, [q, n, k, answer])
        # print(q, n, k, answer)
        assert (q, n, k) not in database.keys()
        database[(q, n, k)] = answer

def construct_db():
    for q in valid_q2end.keys():
        content = get_content(q)
        print(q, "content obtained")
        extract_tables(content)
        print(q, "finished")
    # extract_tables("")
    print("number of items", len(database)) # 151578
    with open('database.json', 'wb') as fout:
        pickle.dump(database, fout, 0)
    print("Done")

def load_test():
    with open('database.json', 'rb') as fin:
        db = pickle.load(fin)
    print(len(db))
    print(list(db.items())[:10])

if __name__ == "__main__":
    load_test()

from gensim.models.word2vec import Word2Vec
import pandas as pd

def DrugId_to_DrugName(drugId):
    drug_to_id_dict = {}
    path = "drugId.txt"
    drug_list = open(path).read().split("\n")
    for line in drug_list:
        id = line.split(" , ")[0]
        name = line.split(" , ")[1]
        if id == drugId:
            drug_to_id_dict[id] = name



def Read_Data():
    result_path = 'Drug_Drug_interaction_Negative.txt'
    file_negative = open(result_path,'w')
    file_negative.write('DrugA,DrugB,Label,Type')

    result_path = 'Drug_Drug_interaction_Positive.txt'
    file_positive = open(result_path, 'w')
    file_positive.write('DrugA,DrugB,Label,Type')

    # drug to id dict
    drug_to_id_dict = {}
    path = "drugId.txt"
    drug_list = open(path).read().split("\n")
    for line in drug_list:
        id = line.split(" , ")[0]
        name = line.split(" , ")[1]
        drug_to_id_dict[id] = name


    # read word2vec model
    model = Word2Vec.load("model.bin")

    # Pnas label list
    label_list = {}
    path = "pnas_1.csv"
    lables = open(path).read().split("\n")
    for type in lables:
        type = type.split(",")
        label_list[type[1]] = type[0]


    # Negative
    Negative_Label = [18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32]

    #create list
    path = "pnas_2.csv"
    file = open(path).read().split("\n")

    negative_Label_Txt = []

    for line in file:
        rel = line.split(",")[0]
        rel_words = rel.split(' ')
        drug_a = ""
        drug_b = ""
        for word in rel_words:
            if word[0:2] == "DB" and drug_a == "":
                drug_a = word.replace(".", "")
            elif word[0:2] == "DB":
                drug_b = word.replace(".", "")

        label1 = rel.replace(drug_a,'Drug a').replace(drug_b,'Drug b')
        label2 = rel.replace(drug_a, 'Drug b').replace(drug_b, 'Drug a')



        label_id = ''
        label_type = ''
        if label1 in label_list:
            label_id = label_list[label1]
            label_type = 'P'
            if int(label_id) in Negative_Label:
                label_type = 'N'
        else:
            label_id = label_list[label2]
            label_type = 'P'
            if int(label_id) in Negative_Label:
                label_type = 'N'

        drug_a_name = ''
        drug_b_name = ''
        if drug_a in drug_to_id_dict and drug_b in drug_to_id_dict:
            drug_a_name = drug_to_id_dict[drug_a].lower()
            drug_b_name = drug_to_id_dict[drug_b].lower()

            if drug_a_name in model.wv.vocab and drug_b_name in model.wv.vocab:
                result = drug_a_name + ',' + drug_b_name + ',' + str(label_id) + ',' + label_type
                if label_type == 'N':
                    file_negative.write('\n' + result)
                if label_type == 'P':
                    file_positive.write('\n' + result)


from selenium import webdriver
def ddi_checker(drug1,drug2):
    url = "G:\\Python37\\webdriver\\chromedriver.exe"
    Chrome = webdriver.Chrome(url)
    Chrome.get('https://www.drugbank.ca/interax/multi_search#results')

    A = Chrome.find_element_by_id("q")
    A.send_keys(drug1 + "; " + drug2)

    A = Chrome.find_element_by_name("button")
    A.click()

    B = Chrome.find_elements_by_tag_name("td")
    if len(B) > 1:
        text = B[1].text.lower().replace(drug1, "").replace(drug2, "")
    else:
        text = ""
    return text


def Recommendation():
    Negative_Label = [18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32]
    Negative_Label_txt = ['no interactin']
    filelabel = pd.read_csv("pnas_1.csv")
    for index,row in filelabel.iterrows():
        if int(row["id"]) in Negative_Label:
            Negative_Label_txt.append(row["text"].replace("Drug a","").replace("Drug b","").lower())

    # read word2vec model
    model = Word2Vec.load("model.bin")

    cluster_drug_list = {}
    drug_cluster_list = {}
    path = 'Drug_Cluster.csv'
    file = pd.read_csv(path)
    for index,row in file.iterrows():
        cluster = row['Cluster Number']
        name = row['Drug Name']
        drug_cluster_list [name] = cluster
        if cluster not in cluster_drug_list:
            cluster_drug_list[cluster] = [name]
        else:
            cluster_drug_list[cluster].append(name)


    pnas_drug_interaction_map = {}
    path = 'Drug_Drug_interaction_Negative.txt'
    file_negative = open(path).read().split('\n')
    del (file_negative[0])

    drug_relation_list = []
    for line in file_negative:
        line = line.split(',')
        if line[0] in drug_cluster_list and line[1] in drug_cluster_list:
            drug_relation_list.append([line[0],line[1]])



    file_result = open("Recommendation_Result_new.txt",'w')
    file_result.write("Drug_1,Drug_2,Drug_1_new,Drug_2_new,Drug_1_new_Similarity,Drug_2_new_Similarity")
    print(drug_relation_list.__len__())
    k= 0
    for item in drug_relation_list:
        k += 1
        print(k)
        if k > 10:
            break
        drug_a = item[0]
        drug_b = item[1]

        drug_a_cluster = drug_cluster_list[drug_a]
        drug_b_cluster = drug_cluster_list[drug_b]

        a_max_similar_number = 0
        a_max_similar_name = ''
        print("a")
        for drug in cluster_drug_list[drug_a_cluster]:
            if drug != drug_b and drug != drug_a and [drug_b,drug] not in drug_relation_list and [drug,drug_b] not in drug_relation_list:
                similarity = model.similarity(drug, drug_a)
                if similarity > a_max_similar_number and similarity >= 0.7 and ddi_checker(drug, drug_b) not in Negative_Label_txt:
                    a_max_similar_number = similarity
                    a_max_similar_name = drug

        b_max_similar_number = 0
        b_max_similar_name = ''
        print("b")
        for drug in cluster_drug_list[drug_b_cluster]:
            if drug != drug_b and drug != drug_a and [drug_a,drug] not in drug_relation_list and [drug,drug_a] not in drug_relation_list:
                similarity = model.similarity(drug,drug_b)
                if similarity > b_max_similar_number and similarity >= 0.7 and ddi_checker(drug, drug_a) not in Negative_Label_txt:
                    b_max_similar_number = similarity
                    b_max_similar_name = drug


        # if a_max_similar_number >= b_max_similar_number and a_max_similar_number >= 0.7:
        #     file_result.write(drug_a + "," + drug_b + "," + a_max_similar_name + "," + drug_b + "," + str(round(a_max_similar_number,3)) + "\n")
        # elif a_max_similar_number < b_max_similar_number and b_max_similar_number >= 0.7:
        #     file_result.write(drug_a + "," + drug_b + "," + drug_a + "," + b_max_similar_name + "," + str(round(b_max_similar_number,3)) + "\n")
        if ddi_checker(a_max_similar_name, b_max_similar_name) not in Negative_Label_txt:
            print(k)
            file_result.write("\n"+drug_a + "," + drug_b + "," +
                              a_max_similar_name + "," + b_max_similar_name + "," +
                              str(round(a_max_similar_number, 3)) + "," +
                              str(round(b_max_similar_number, 3)))


Recommendation()

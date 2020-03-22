
data_Interactions = open("Pnas_DDI_Dataset.csv").read().split("\n")


X_Data = []
Y_Data = []


data_Labels = {}
index = 0

for rows in data_Interactions:
    Line = rows.split(",")
    Interaction = Line[0]
    Type = Line[1]

    Drugs = []
    for word in Interaction.split(" "):
        if word[0:2] == "DB":
            Drugs.append(word)

    Drugs = list(set(Drugs))

    Drug_A = Drugs[0].replace(".","")
    Drug_B = Drugs[1].replace(".","")

    Interaction = Interaction.replace(Drug_A,"")
    Interaction = Interaction.replace(Drug_B,"")

    if Interaction in data_Labels:
        Label_index = data_Labels[Interaction]
    else:
        index += 1
        data_Labels[Interaction] = index
        Label_index = index

    print(Interaction)
    print(Label_index)






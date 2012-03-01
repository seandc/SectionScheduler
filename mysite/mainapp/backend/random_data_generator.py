from random import random
TIMES = [
'Mondays 4:00 pm-5:00 pm',
'Mondays 5:00 pm-6:00 pm',
'Mondays 6:00 pm-7:00 pm',
'Mondays 7:00 pm-8:00 pm',
'Mondays 8:00 pm-9:00 pm',
'Tuesdays 10:00 am-11:00 am',
'Tuesdays 11:00 am-12:00 noon',
'Tuesdays 12:00 noon-1:00 pm',
'Tuesdays 1:00 pm-2:00 pm',
'Tuesdays 2:00 pm-3:00 pm',
'Wednesdays 9:00 am-10:00 am',
'Wednesdays 10:00 am-11:00 am',
'Wednesdays 11:15 am-12:15 pm',
'Wednesdays 12:30 pm-1:30 pm',
]

FEMALE_NAMES = [
'Selena Maust',
'Jami Patron',
'Benita Strum',
'Ericka Munsch',
'Ashlee Rhymes',
'Loraine Senior',
'Liza Lino',
'Jeanie Oullette',
'Loraine Plata',
'Liebman',
'Kathrine Runions',
'Alejandra Raabe',
'Noemi Tilson',
'Dona Gaut',
'Roxie Manross',
'Pearlie Sant',
'Saundra Shetley',
'Milagros Twiss',
'Dona Verdun',
'Gay Elling',
'Roslyn Tito',
'Selena Kinsel',
'Hillary Kuder',
'Tanisha Streich',
'Althea Westray',
'Penelope Blanch',
'Jami Hottinger',
'Rae Shorey',
'Karina Bowersox',
'Ericka Maday',
'Capito',
'Tabatha Bevill',
'Louisa Loughran',
'Noreen Fenley',
'Pearlie Rather',
'Selena Treese',
'Ashlee Messinger',
'Alejandra Elbert',
'Karina Hazlitt',
'Tanisha Harford',
'Darcy Oren',
'Althea Kieser',
'Nita Stelter',
'Athey',
'Lilia Gourd',
'Penelope Lighty',
'Neva Defibaugh',
'Tia Steves',
'Selena Jennette',
'Roxie Shira',
'Tia Schueller',
'Benita Roling',
'Edwina Court',
'Marylou Tippie',
'Alejandra Commander',
'Neva Hillier',
'Rae Sanmartin',
'Marcie Onstad',
'Saundra Kampen',
'Elinor Lapeyrouse',
'Mcghie',
'Switalski',
'Alana Sprau',
'Lilia Mercure',
'Lorrie Hail',
'Penelope Granberry',
'Lenore Chamorro',
'Esmeralda Donmoyer',
'Julianne Nuzzo',
'Nita Tsan',
'Edwina Junker',
'Malinda Shadley',
'Harriett Bilderback',
'Liza Maser',
'Lorrie Petrowski',
'Lakisha Brugger',
'Hillary Mance',
'Neva Pruden',
'Maricela Elkin',
'Alana Durfey',
'Marylou Strout',
'Carlene Royalty',
'Lilia Quast',
'Alejandra Smyers',
'Darcy Selleck',
'Mallory Min',
'Noemi Vitello',
'Earnestine Hackathorn',
'Hillary Winningham',
'Rae Duchene',
]

MALE_NAMES = [
'KELLY Houchin',
'GUY Allmond',
'LANCE Janis',
'TED Bergner',
'MATHEW Matzen',
'DARRYL Brackman',
'CODY Eastridge',
'LONNIE Alamo',
'KELLY Bedoya',
'KELLY Nery',
'KELLY Lassonde',
'MAX Demaray',
'KURT Breck',
'JESSIE Ickes',
'KELLY Caplan',
'MAX Roig',
'MAX Eriksson',
'MATHEW Tepper',
'ALLAN Kennan',
'ERIK Coppage',
'DARRYL Likes',
'TYRONE Nishida',
'CLINTON Aune',
'HUGH Alcott',
'GUY Brier',
'JULIO Beahm',
'CHRISTIAN Costilla',
'NEIL Burkhead',
'JULIO Voisine',
'GUY Reves',
'ALLAN Yeadon',
'KELLY Lisa',
'GUY Rolfes',
'CHRISTIAN Knudtson',
'CHRISTIAN Kincade',
'JAMIE Detweiler',
'CLINTON Pawlowski',
'JULIO Columbia',
'NEIL Scholes',
'DARREN Arney',
'NEIL Ruple',
'CODY Harshaw',
'TED Huguley',
'CLAYTON Kreitzer',
'DARRYL Cebula',
'GUY Jeske',
'TYRONE Cantero',
'FERNANDO Verner',
'KELLY Marie',
'KELLY Dade',
'TYRONE Pollan',
'CODY Hermsen',
'KELLY Topper',
'MATHEW Nantz',
'KELLY Veazey',
'DARRYL Schwalb',
'LONNIE Vicario',
'ERIK Vashon',
'KURT Yardley',
'JAMIE Manwaring',
'KURT Parrilla',
'NELSON Bad',
'JULIO Clinkscales',
'DARRYL Shehorn',
'TYRONE Provenza',
'CLAYTON Soltani',
'MAX Erhart',
'NEIL Marple',
'CLINTON Carasco',
'LANCE Trollinger',
'DARRYL Greg',
'JULIO Lawley',
'CLINTON Kruckeberg',
'NEIL Propp',
'JAVIER Nishimoto',
'TED Most',
'ALLAN Lanctot',
'KELLY Boniello',
'NELSON Spino',
'HUGH Reimann',
'KURT Dupuy',
'CODY Vanscoy',
'NELSON Segers',
'GUY Wickwire',
'GUY Speno',
'JAMIE Malchow',
'CHRISTIAN Pichette',
'JAVIER Peri',
'KURT Raskin',
'TED Culligan',
]

def make_random_student_table(p_of_male, p_of_availability, number_of_tas, total_number):
    male_index = 0
    female_index = 0
    data = {}
    for i in range(total_number):
        student = {}
        if random() < p_of_male:
            name = MALE_NAMES[male_index]
            male = 'True'
            male_index += 1
        else:
            name = FEMALE_NAMES[female_index]
            male = 'False'
            female_index += 1
        student['section_availability_ordered'] = [time for time in TIMES if random() < p_of_availability]
        student['is_male'] = male
        student['is_ta'] = 'True' if i < number_of_tas else 'False'
        student['cant_be_with'] = []
        data[name] = student
    return data




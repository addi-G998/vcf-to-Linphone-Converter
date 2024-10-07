import os
import sqlite3
import quopri

def read_vcf_file(file_path):
    records = []
    with open(file_path, 'r') as vcf_file:
        record = {}
        for line in vcf_file:
            line = line.strip()
            if line.startswith('BEGIN:VCARD'):
                record = {}
            elif line.startswith('END:VCARD'):
                records.append(record)
            elif ':' in line:
                key, value = line.split(':', 1)
                record[key] = value
    return records

def retrieveLastID(con):
    cursor = con.cursor()
    cursor.execute("SELECT id FROM friends ORDER BY id DESC LIMIT 1")
    last_id = cursor.fetchone()
    return last_id[0] if last_id else None

def add_new_users(con, new_id, name, number):
    cursor = con.cursor()
    user = name
    phoneNumber = number
    cursor.execute(
        "INSERT INTO friends(id, friend_list_id, sip_uri,subscribe_policy,send_subscribe,vCard,presence_received)  VALUES (?,1,'\"'||?||'\" <sip:'||?||'@sipurl>',1,0,'BEGIN:VCARD VERSION:4.0 IMPP:sip:'||?||'@sipurl FN:'||?||' END:VCARD',0);",
        (new_id, user, phoneNumber, phoneNumber, user))
    con.commit()

def decodeUTF(encodedText):

    decoded_text = quopri.decodestring(encodedText)
    if len(decoded_text) > 1 and decoded_text[-2] >= 0xc0:
        decoded_text = decoded_text[:-2]
    elif decoded_text[-1] >= 0xc0:
        decoded_text = decoded_text[:-1]
    decoded_text = decoded_text.decode('utf-8')
    return decoded_text

def parseToLinphone():
    username = os.getlogin()
    dbfile = "C:/Users/" + username + "/AppData/Local/linphone/friends.db"
    con = sqlite3.connect(dbfile)


    for record in vcf_records:
        #if record == {'VERSION': '2.1'} or {'VERSION': '4.0'}:
            #continue
        name = record.get('FN')
        if name is None:
            name = decodeUTF(record.get('FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE') or record.get(
        'N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE'))
        print("Name:", name)
        tel_numbers = record.get('TEL;X-Mobil') or record.get('TEL;:') or record.get('TEL;')or record.get('TEL:') or record.get('TEL;CELL') or record.get('TEL;X-Benutzerdefiniert') or record.get('TEL;WORK') or record.get('PHONE')  # Adjust property names as needed
        tel_private = record.get('TEL;X-Privat') or record.get('TEL;PREF') or record.get('TEL;CELL;PREF') or record.get('PHONE.CELL')

        rmchar = "-"
        rmspace = " "
        if tel_numbers is not None:
            tel_numbers = tel_numbers.replace(rmchar, "")
            tel_numbers = tel_numbers.replace(rmspace, "")
        if tel_private is not None:
            tel_private = tel_private.replace(rmchar, "")
            tel_private = tel_private.replace(rmspace, "")

        if tel_numbers:
            print("Phone:", tel_numbers)
        if tel_private:
            print("Privat:", tel_private)
        print("-" * 20)

        validNumber = None
        if name and (tel_numbers or tel_private) is not None:
            if tel_numbers is None:
                validNumber = tel_private
            else:
                validNumber = tel_numbers
        if validNumber is None:
            continue
        new_id = retrieveLastID(con) + 1
        add_new_users(con, new_id, name, validNumber)

    con.close()

if __name__ == '__main__':


    vcf_records = read_vcf_file('/Location/of/your/vcf/file')
    parseToLinphone()
    # Now you can access the parsed records







#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
from psycopg2.extras import Json
import xml.etree.ElementTree as ET
import os
import re
import sys
import xmltodict
import xml
import json
import codecs


# Database Connection Settings (Change as Needed)
db_host = "localhost"
db_user = "ct"
db_name = "ct"
# End config


db_con = None
xsd = None
force_list_list = []

def main(path):
    global xsd
    global force_list_list
    global db_con

    # set up the database tables
    ns = { 'xs': 'http://www.w3.org/2001/XMLSchema' }
    xsd = ET.parse('public.xsd').getroot()
    csDef = xsd.find("xs:element[@name='clinical_study']", ns)
    force_list_list = list_elements(csDef, ['clinical_study'])
    db_con = psycopg2.connect(host=db_host, user=db_user, dbname= db_name)
    init_db(top_level_elements(csDef))

    # parse and insert clinical_study data from xml
    xmls = get_all_xmls(path);
    for i in range(len(xmls)):
        add_study(read2dict(xmls[i]))
        sys.stdout.write("\r{}/{}".format(i+1, len(xmls)))
        sys.stdout.flush()

    print " ...done"



# return a list of elements that should be represented as lists
def list_elements(elem, path=[]):
    return_vals = []
    for child in list(elem):
        name = child.get('name')

        type = child.get('type') or child.get('base')
        unbounded = child.get("maxOccurs") == "unbounded"
        newPath = list(path)
        typeDef = None
        if type is not None:
            typeDef = xsd.find("*[@name='{}']".format(type))
        if name is not None:
            newPath.append(name)
        if unbounded:
            if newPath not in return_vals:
                return_vals.append(newPath)
        # recurse over type definition if it exists
        if typeDef is not None:
            from_type = list_elements(typeDef, newPath)
            if len(from_type) > 0:
                return_vals += from_type
        # recurse over children
        from_children = list_elements(child, newPath)
        if len(from_children) > 0:
            return_vals += from_children
    return return_vals


def top_level_elements(elem):
    return [e.get('name') for e in elem.findall(".//{http://www.w3.org/2001/XMLSchema}element")]



def should_force_list(path,key,value):
    path = [p[0] for p in path]
    path.append(key)
    ret = (path in force_list_list)
    return ret



def init_db(columns):
    cur = db_con.cursor()
    cur.execute("DROP TABLE IF EXISTS cs")
    column_defs = ['id serial PRIMARY KEY']
    for c in columns:
        column_defs.append(c + ' jsonb')
    cur.execute("CREATE TABLE cs ({});".format(', '.join(column_defs)))
    db_con.commit()
    cur.close()


def add_study(s):
    cur = db_con.cursor()
    cols = []
    vals = []
    for k,v in s['clinical_study'].items():
        cols.append(k)
        vals.append(Json(v, dumps=json.dumps))
    cols = ', '.join(cols)
    v_placeholder =  ', '.join(['%s']*len(vals))
    sql = "INSERT INTO cs ({}) VALUES ({});".format(cols, v_placeholder)
    cur.execute(sql, vals)
    db_con.commit()
    cur.close()



def read2dict(file):
    try:
        with codecs.open(file, encoding='utf-8', mode='r') as myfile:
            data=myfile.read()
        return xmltodict.parse(data, force_list=should_force_list)
    except xml.parsers.expat.ExpatError as e:
        print "Parse error in {}: {} ".format(file, e)
        exit(1)
    return tree.getroot()


# get list of xml files in subfolders of a_dir
def get_all_xmls(a_dir):
    xmls = []
    for f in get_folders(a_dir):
        xmls.extend(get_xml_files(f))
    return xmls

# get list of subfolders in a_dir
def get_folders(a_dir):
    return [os.path.join(a_dir, name) for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


# get list of xml files in a_dir
def get_xml_files(a_dir):
    return [os.path.join(a_dir, name) for name in os.listdir(a_dir)
        if (re.match('.*\.xml', name)
            and os.path.isdir(os.path.join(a_dir, name)) == False) ]




if __name__ == '__main__':
    main(sys.argv[1])

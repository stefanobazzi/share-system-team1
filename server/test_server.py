#!/usr/bin/env python
#-*- coding: utf-8 -*-

import server
import os
import string
import json
import random
import unittest
import shutil
from base64 import b64encode

TEST_DIRECTORY = "test_users_dirs/"
TEST_USER_DATA = "test_user_data.json"

DEMO_USER = "i_am_an_user@rawbox.it"
DEMO_PSW = "very_secret_password"
DEMO_HEADERS = {
    "Authorization": "Basic " + b64encode("{0}:{1}".format(DEMO_USER, DEMO_PSW))
}
DEMO_FILE = "somefile.txt"
DEMO_PATH = "somepath/somefile.txt"
DEMO_CONTENT = "Hello my dear,\nit's a beautiful day here in Compiobbi."


def create_demo_user(user=None, psw=None):
    if not user:
        random.seed(10)
        user = "".join(random.sample(string.letters, 5))
    if not psw:
        random.seed(10)
        psw = "".join(random.sample(string.letters, 5))

    with server.app.test_client() as tc:
        return tc.post("/API/v1/create_user",
                data = {
                    "user" : user,
                    "psw" : psw
                }
        )


class TestSequenceFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # set a test "USERS_DIRECTORIES"
        try:
            os.mkdir(TEST_DIRECTORY)
        except OSError:
            shutil.rmtree(TEST_DIRECTORY)
            os.mkdir(TEST_DIRECTORY)

        server.USERS_DIRECTORIES = TEST_DIRECTORY
    
        # set a test "USER_DATA" json
        open(TEST_USER_DATA, "w").close()
        server.USERS_DATA = TEST_USER_DATA

        # demo user configuration
        create_demo_user(DEMO_USER, DEMO_PSW)
        with open(DEMO_FILE, "w") as f:
            f.write(DEMO_CONTENT)


    @classmethod
    def tearDownClass(cls):
        # restore previous status
        os.remove(DEMO_FILE)
        os.remove(TEST_USER_DATA)
        shutil.rmtree(TEST_DIRECTORY)


    def setUp(self):
        server.app.config.update(TESTING=True)
        server.app.testing = True
    

    # check if a new user is correctly created
    def test_correct_user_creation(self):
        dirs_counter = len(os.listdir(server.USERS_DIRECTORIES))
        with server.app.test_client() as tc:
            rv = create_demo_user()
            self.assertEqual(rv.status_code, server.HTTP_CREATED)
        
        # check if a directory is created
        new_counter = len(os.listdir(server.USERS_DIRECTORIES))
        self.assertEqual(dirs_counter+1, new_counter)


    # check if, when the user already exists, 'create_user' returns an error
    def test_user_who_already_exists(self):
        user = "Gianni"
        psw = "IloveJava"
        with server.app.test_client() as tc:
            create_demo_user(user, psw)
            rv = create_demo_user(user, psw)
            self.assertEqual(rv.status_code, server.HTTP_CONFLICT)


    def test_to_md5(self):
        # check if two files with the same content have the same md5        
        second_file = "second_file.txt"
        with open(second_file, "w") as f:
            f.write(DEMO_CONTENT)

        first_md5 = server.to_md5(DEMO_FILE)
        second_md5 = server.to_md5(second_file)
        self.assertEqual(first_md5, second_md5)

        os.remove(second_file)

        # check if, for a directory, returns False
        tmp_dir = "aloha"
        os.mkdir(tmp_dir)
        self.assertFalse(server.to_md5(tmp_dir))

        os.rmdir(tmp_dir)


    def test_files_post(self):
        f = open(DEMO_FILE, "r")
        with server.app.test_client() as tc:
            rv = tc.post(
                "{}files/{}".format(server._API_PREFIX, DEMO_PATH),
                headers = DEMO_HEADERS,
                data = { "file_content": f }
            )
            self.assertEqual(rv.status_code, 201)
        f.close()
        with open("{}{}/{}".format(TEST_DIRECTORY, DEMO_USER, DEMO_PATH)) as f:
            uploaded_content = f.read()
            self.assertEqual(DEMO_CONTENT, uploaded_content)


    def test_files_get(self):
        client_path = os.path.join("prr", DEMO_FILE)
        server_path = os.path.join(TEST_DIRECTORY, DEMO_USER, client_path)
        os.makedirs(os.path.dirname(server_path))
        shutil.copy(DEMO_FILE, server_path)

        server.User.users[DEMO_USER].paths[client_path] = [server_path, 0, 0]

        with server.app.test_client() as tc:
            rv = tc.get(
                "{}files/{}".format(server._API_PREFIX, client_path),
                headers = DEMO_HEADERS
            )
            self.assertEqual(rv.status_code, 200)
        
        with open(server_path) as f:
            got_content = f.read()
            self.assertEqual(DEMO_CONTENT, got_content)


if __name__ == '__main__':
    # make tests!
    unittest.main()

import sys
import os

import psycopg2
import logging
from collections import namedtuple

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'../../','util'))

from DatabaseCon import DatabaseCon


edit = namedtuple('edit', ['project', 'file_name', 'is_test','sha', 'commit_date', 'isbug'])

class edit(namedtuple('edit', ['project', 'file_name', 'is_test','sha', 'commit_date', 'isbug'])):
    __slots__ = ()

    def __repr__(self):
        return "%s|%s|%s|%s|%s\n" % (self.file_name, self.is_test, self.sha, self.commit_date, self.isbug)

	def getCommitDate(self):
		return self.commit_date.split(" ")[0]


class DbEdits:

	def __init__(self, proj, lang):
		self.project = proj
		self.language = lang
		self.edits = []

	def __str__(self):

		print_str = ""
		for e in self.edits:
			print_str += str(e)

		return print_str

	def connectDb(self, db, dbUser, dbHost, dbPort):

		self.dbCon = DatabaseCon(db, dbUser, dbHost, dbPort)

	def fetchEditsFromTable(self, table):

		sql_command = "SELECT project, file_name, sha, commit_date, isbug, is_test "
		sql_command +=  " FROM " + table + " WHERE tag = \'" + self.language + \
						"\' and project = \'" + self.project + "\'"

		print sql_command
		
		rows = self.dbCon.execute(sql_command)

		for row in rows:
			project, file_name, sha, commit_date, isbug, is_test = row
			e = edit(project, file_name, is_test, sha, commit_date, isbug)
			self.edits.append(e)


	def printEdits(self):

		for e in self.edits:
			print e

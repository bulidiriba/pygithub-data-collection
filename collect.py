#!/usr/bin/env python
from github import Github
import argparse
import sys
import os

class Collect():
	def __init__(self):
		self.user=''
		self.pwd=''
		self.token=''
		self.org=''
		self.repo=''
		self.branch=''
		self.event_type=''
		self.per_page=100

	def get_arguments(self):
		parser = argparse.ArgumentParser(description="Github data collection with PyGithub")
		parser.add_argument('--user', type=str, help="The name of the user")
		parser.add_argument('--pwd', type=str,  help="Password of the user")
		parser.add_argument('--token', type=str, help="The private token of the user")
		parser.add_argument('--org', type=str,  help="The name of the Organization")
		parser.add_argument('--repo', type=str,  help="The name of the Repositories")
		parser.add_argument('--branch',  type=str, help="The name of the branches")
		parser.add_argument('--event_type', type=str, help="The type of the events(e.g issues, commits")
		parser.add_argument('--per_page', default=self.per_page,  type=int, help="The number of per_page requests")

		return parser.parse_args()

	def validate_arguments(self, args):
		"""Validate arguments entered by user"""
		if args.user == None:
			print('Please specify your github user name. Exiting.')
			sys.exit(0)
		if args.pwd == None:
			print('Please specify your password. Exiting.')
			sys.exit(0)
		if args.org == None:
			print('Please specify Organization name. Exiting.')
			sys.exit(0)
		if args.event_type == None:
			print('Please specify type of the event. Exiting.')
			sys.exit(0)
		return

	def identify_event(self,args):
		"""identify the type of event given by the user"""
		if(args.event_type == 'issues'):
			self.collect_issues(args)
		if(args.event_type == 'issue_comments'):
			self.collect_issue_comments(args)
		if(args.event_type == 'commits'):
			pass


	def create_directory(self,args):
		"""Create a directory for organization, for each repository in organization, for each event type in repository"""
		client = Github(args.user, args.pwd, per_page=args.per_page)
		orgn = client.get_organization(args.org)

		# 1... create a directory for this organization
		if not os.path.exists(args.org):
			os.mkdir(args.org)

		# 2... create directory for each repository of an organization

		# get repository
		repo_list = []
		if (args.repo == 'all'):
			repo_list = [repo.name for repo in orgn.get_repos()]
		else:
			repo_list = [args.repo]

		# create direcory
		for j in repo_list:
			if not os.path.exists(args.org + "/" + j):
				os.mkdir(args.org + "/" + j)

		# 3.... create directory for each event type of repository
		for repo_name in repo_list:
			if not os.path.exists(args.org+"/"+repo_name+"/"+args.event_type):
				os.mkdir(args.org+"/"+repo_name+"/"+args.event_type)


	def get_repo(self,args):
		"""store all repository in a given organization as repo_list"""
		client = Github(args.user,args.pwd,  per_page=args.per_page)
		orgn = client.get_organization(args.org)

		repo_list=[]
		if(args.repo == 'all'):
			repo_list = [repo.name for repo in orgn.get_repos()]
		else:
			repo_list = [args.repo]

		return repo_list

	def collect_issues(self, args):
		"""collect the data of the issue event in a given repository may be all repository or one repository"""
		client = Github(args.user,args.pwd, per_page=args.per_page)
		orgn = client.get_organization(args.org)

		# first call a create directory function
		self.create_directory(args)

		# then call a get_repo function
		repo_list = self.get_repo(args)

		try:
			for repo_name in repo_list:
				repo = orgn.get_repo(repo_name)
				issue_list = []
				for issue in repo.get_issues():
					issue_dict = {}
					issue_dict['number'] = issue.number
					issue_dict['id'] = issue.id
					issue_dict['user'] = issue.user
					issue_dict['title'] = issue.title
					issue_dict['body'] = issue.body
					issue_dict['url'] = issue.url
					issue_dict['milestone'] = issue.milestone
					issue_dict['labels'] = issue.labels
					issue_dict['labels_url'] = issue.labels_url
					issue_dict['created_at'] = issue.created_at
					issue_dict['updated_at'] = issue.updated_at
					issue_dict['closed_at'] = issue.closed_at
					issue_dict['closed_by'] = issue.closed_by
					issue_dict['pull_request'] = issue.pull_request
					issue_dict['state'] = issue.state
					issue_dict['events_url'] = issue.events_url
					issue_dict['number_of_comments'] = issue.comments
					issue_dict['comments_url'] = issue.comments_url
					issue_list.append(issue_dict)


					with open(args.org+"/"+repo_name+"/"+args.event_type+"/open_issues.json", 'w') as f:
						f.write(str(issue_list))
			print("data successfully collected")
		except Exception as e:
			print("Problem Occured: ", e)

		def collect_issue_comments(self, args):
			pass

		def collect_commits(self,args):
			pass


	def main(self):
		# get the arguments from the terminal
		args = self.get_arguments()

		# validate the given arguments
		self.validate_arguments(args)

		# identify the event type needed by the user and then go forward
		self.identify_event(args)


# Initialize the class
collect = Collect()
collect.main()
#!/usr/bin/env python
from github import Github
import argparse
import sys
import os
import time
import random


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
		self.client=''
		self.organization=''
		self.state=''
		self.sleep_time_length = 1 #5
		self.sleep_time_range = 1 #3

	def get_arguments(self):
		parser = argparse.ArgumentParser(description="Github data collection with PyGithub")
		parser.add_argument('--user', type=str, help="The name of the user")
		parser.add_argument('--pwd', type=str,  help="Password of the user")
		parser.add_argument('--token', type=str, help="The private token of the user")
		parser.add_argument('--org', type=str,  help="The name of the Organization")
		parser.add_argument('--repo', type=str,  help="The name of the Repositories")
		parser.add_argument('--branch',  type=str, help="The name of the branches")
		parser.add_argument('--state',  type=str, help="The State of the issues")
		parser.add_argument('--event_type', type=str, help="The type of the events(e.g issues, commits")
		parser.add_argument('--per_page', default=self.per_page,  type=int, help="The number of per_page requests")
		return parser.parse_args()

	def validate_arguments(self, args):
		"""Validate arguments entered by user"""
		if args.org == None:
			print('Please specify Organization name. Exiting.')
			sys.exit(0)
		if args.repo == None:
			print('Please specify Repositories name. Exiting.')
			sys.exit(0)
		if args.event_type == None:
			print('Please specify type of the event. Exiting.')
			sys.exit(0)
		if args.event_type == 'commits' and args.branch == None:
			print('Please specify branch name. Exiting.')
			sys.exit(0)
		if args.event_type == 'issues' and args.state == None:
			print('Please specify state of the issues. Exiting.')
			sys.exit(0)
		if args.event_type == 'pullRequests' and args.branch == None and args.state == None:
			print('Please specify branch and state of the pulls. Exiting.')
			sys.exit(0)
			
		return

	def create_github_instance(self, args):
		if args.token != None:
			#client = Github(args.token, per_page=args.per_page)
			#self.client = Github(args.user, args.pwd, per_page=args.per_page)
			self.client = Github(args.user, login_or_token=args.token, per_page=args.per_page)
			
		elif args.user != None and args.pwd != None:
			self.client = Github(args.user, args.pwd, per_page=args.per_page)

		else:
			self.client = Github()		

		self.organization = self.client.get_organization(args.org)

	def create_directory(self,args):
		"""Create a directory for organization, for each repository in organization, for each event type in repository"""
		# 1... create a directory for this organization
		if not os.path.exists(args.org):
			os.mkdir(args.org)
		# 2... create directory for each repository of an organization
		# get repository

		repo_list = []
		if (args.repo == 'all'):
			repo_list = [repo.name for repo in self.organization.get_repos()]
		else:
			repo_list = [args.repo]

		# create direcory
		for j in repo_list:
			if not os.path.exists(args.org + "/" + j):
				os.mkdir(args.org + "/" + j)

		# 3.... create directory for each event type of repository
		for repo_name in repo_list:
			if args.event_type == 'commits':
				branch_name_list = self.get_branch(repo_name, args)
				for branch_name in branch_name_list:
					if not os.path.exists(args.org+"/"+repo_name+"/"+args.event_type + "/"+ branch_name + "_branch"):
						os.mkdir(args.org+"/"+repo_name+"/"+args.event_type + "/"+ branch_name + "_branch")
			else:
				if not os.path.exists(args.org+"/"+repo_name+"/"+args.event_type):
					os.mkdir(args.org+"/"+repo_name+"/"+args.event_type)

	def identify_event(self,args):
		"""identify the type of event given by the user"""
		if(args.event_type == 'issues'):
			self.collect_issues(args)
		if(args.event_type == 'issues_comments'):
			self.collect_issues_comments(args)
		if (args.event_type == 'issues_events'):
			self.collect_issues_events(args)
		if (args.event_type == 'commits'):
			self.collect_commits(args)
		if (args.event_type == 'events'):
			self.collect_events(args)
		if(args.event_type == 'pullRequests'):
			self.collect_pullRequests(args)
		if (args.event_type == 'pullRequestComments'):
			self.collect_pullRequestComments(args)
    
	def get_repo(self,args):
		"""store all repository in a given organization as repo_list"""
		repo_list=[]
		if(args.repo == 'all'):
			repo_list = [repo.name for repo in self.organization.get_repos()]
		else:
			repo_list = [args.repo]

		return repo_list
    
	def get_branch(self, repo_name, args):
		branch_list =[]
		if(args.branch == 'all'):
			branch_list = [branch.name for branch in self.organization.get_repo(repo_name).get_branches()]

		else:
			branch_list = [args.branch]

		return branch_list

	def collect_issues_events(self, args):
		repo_list = self.get_repo(args)
		print(repo_list)
		try:
			for repo_name in repo_list:
				repo = self.organization.get_repo(repo_name)
				issues_events_list = []
				num_of_issues_events = 0
				for event in repo.get_issues_events():
					event_dict = {}
					event_dict['actor'] = event.actor
					event_dict['commit_id'] = event.commit_id
					event_dict['created_at'] = event.created_at
					event_dict['event'] = event.event
					event_dict['id'] = event.id
					event_dict['issue'] = event.issue
					event_dict['url'] = event.url
					event_dict['node_id'] = event.node_id
					event_dict['commit_url'] = event.commit_url
					event_dict['label'] = event.label
					event_dict['assignee'] = event.assignee
					issues_events_list.append(event_dict)

					num_of_issues_events += 1
					print(num_of_issues_events)

				self.sleeper()
				print(issues_events_list)
				with open(args.org + "/" + repo_name + "/" + args.event_type + "/" + args.org + "-" + repo_name + "-" +
                          args.event_type + ".json", 'w') as f:
						f.write(str(issues_events_list))
			print("data successfully collected")
		except Exception as e:
			print("Problem Occured: ", e)

	def collect_pullRequests(self, args):
		# call a get_repo function
		repo_list = self.get_repo(args)
		print(repo_list)
		try:
			for repo_name in repo_list:
				repo = self.organization.get_repo(repo_name)
				branch_list = self.get_branch(repo_name, args)
				print("branches: ", branch_list)
				for branch in branch_list:
				    pull_list = []
				    num_of_pulls = 0
				    for pull in repo.get_pulls(state=args.state, sort='created', base=branch):
					    pull_dict = {}
					    pull_dict['id'] = pull.id
					    pull_dict['number'] = pull.number
					    pull_dict['title'] = pull.title
					    pull_dict['user'] = pull.user
					    pull_dict['body'] = pull.body
					    pull_dict['changed_files'] = pull.changed_files
					    pull_dict['closed_at'] = pull.closed_at
					    pull_dict['comments'] = pull.comments
					    pull_dict['commits'] = pull.commits
					    pull_dict['created_at'] = pull.created_at
					    pull_dict['commits_url'] = pull.commits_url
					    pull_dict['review_comments'] = pull.review_comments
					    pull_dict['head'] = pull.head
					    pull_dict['merged'] = pull.merged
					    pull_dict['merged_at'] = pull.merged_at
					    pull_dict['merged_by'] = pull.merged_by
					    pull_dict['milestone'] = pull.milestone
					    pull_dict['merge_commit_sha'] = pull.merge_commit_sha
					    pull_dict['mergeable'] = pull.mergeable
					    pull_dict['mergeable_state'] = pull.mergeable_state
					    pull_dict['labels'] = pull.labels
					    pull_dict['deletions'] = pull.deletions
					    pull_dict['additions'] = pull.additions
					    pull_dict['commit_url'] = pull.commits_url
					    pull_dict['assignee'] = pull.assignee
					    pull_dict['assignees'] = pull.assignees
					    pull_dict['base'] = pull.base
					    pull_list.append(pull_dict)
					    num_of_pulls += 1
					    print(num_of_pulls)

				    self.sleeper()
				    print(pull_list)
				    with open(args.org + "/" + repo_name + "/" + args.event_type + "/" + args.org + "-" + repo_name + "-" +
						        branch + "-" + args.state + "-" + args.event_type + ".json", 'w') as f:
					      f.write(str(pull_list))
			print("data successfully collected")
		except Exception as e:
			print("Problem Occured: ", e)

	def collect_pullRequestComments(self,args):
	# call a get_repo function
		repo_list = self.get_repo(args)
		print(repo_list)
		try:
			for repo_name in repo_list:
				repo = self.organization.get_repo(repo_name)
				pull_list = []
				num_of_pulls = 0
				for pull in repo.get_pulls_comments():
				    pull_dict = {}
				    pull_dict['id'] = pull.id
				    pull_dict['user'] = pull.user
				    pull_dict['body'] = pull.body
				    pull_dict['created_at'] = pull.created_at
				    pull_dict['commit_id'] = pull.commit_id
				    pull_dict['created_at'] = pull.created_at
				    pull_dict['diff_hunk'] = pull.diff_hunk
				    pull_dict['in_reply_to_id'] = pull.in_reply_to_id
				    pull_dict['pull_request_url'] = pull.pull_request_url

				    pull_list.append(pull_dict)
				    num_of_pulls += 1
				    print(num_of_pulls)
				# finalissue = "\n".join(str(row) for row in issue_list)
				with open(args.org + "/" + repo_name + "/" + args.event_type + "/" + args.org + "-" + repo_name + "-" +
				          args.event_type + ".json", 'w') as f:
					f.write(str(pull_list))
				print("data successfully collected")
		except Exception as e:
			print("Problem Occured: ", e)

	def collect_commits(self, args):
		"""collect the data of the issue event in a given repository may be all repository or one repository"""
		# call a get_repo function
		repo_list = self.get_repo(args)
		print("\nRepositories: ", repo_list)
		try:
			for repo_name in repo_list:
				repo = self.organization.get_repo(repo_name)
				branch_list = self.get_branch(repo_name, args)
				print("branches: ", branch_list)
				
				for branch in branch_list:
					git_branch = self.organization.get_repo(repo_name).get_branch(branch)
					branch_commit = git_branch.commit
	
					total_commits = repo.get_commits(sha=branch_commit.sha).totalCount
					print("total commits in ",branch," branch is: ", total_commits)

					# since there are 100 commits in a single page we can easily get the total number of page by dividing the total commits with 100
					total_page =  int(total_commits / 100)
					print("The total number of page is: " + str(total_page))

					#print(repo.get_commits().get_page(rel='last'))
					page = 0
					num_of_commits = 0
					while page <= 5:#just for testing but actually its till last page
						commit_list = []
						print("page: ", page)
						
						for commit in repo.get_commits(sha=branch_commit.sha).get_page(page):
							commit_dict = {}
							commit_dict['author'] = commit.author
							commit_dict['sha'] = commit.sha
							#commit_dict['files'] = commit.files
							#commit_dict['stats'] = commit.stats
							# commit_dict['commit'] = commit.commit
							# commit_dict['committer'] = commit.committer
							# commit_dict['comments_url'] = commit.comments_url
							# commit_dict['html_url'] = commit.html_url
							# commit_dict['parents'] = commit.parents
							# commit_dict['url'] = commit.url
							commit_list.append(commit_dict)

							num_of_commits += 1
							print(num_of_commits)

                        

						self.sleeper()
						print(commit_list)
						with open(args.org + "/" + repo_name+"/"+args.event_type+"/"+branch+"_branch/" +  args.org + "-" +
					 		repo_name + "-"+branch+"_branch-" + args.event_type + "-page-" + str(page) + ".json", 'w') as f:
							f.write(str(commit_list))


						page += 1
						commit_list = []
			print("commit data successfully collected")
		except Exception as e:
			print("Problem Occured: ", e)

	def collect_commits_comments(self, args):
		pass

	def collect_events(self, args):
		# call a get_repo function
		repo_list = self.get_repo(args)
		print(repo_list)
		try:
			for repo_name in repo_list:
				repo = self.organization.get_repo(repo_name)
				event_list = []
				num_of_events = 0
				for event in repo.get_events():
					event_dict = {}
					event_dict['actor'] = event.actor
					event_dict['id'] = event.id
					event_dict['payload'] = event.id
					event_dict['created_at'] = event.created_at
					event_dict['org'] = event.org
					event_dict['public'] = event.public
					event_dict['repo'] = event.repo
					event_dict['type'] = event.type
					event_list.append(event_dict)

					num_of_events += 1
					print(num_of_events)

				# finalissue = "\n".join(str(row) for row in issue_list)
				with open(args.org + "/" + repo_name + "/" + args.event_type + "/" + args.org + "-" + repo_name + "-" +
						  args.event_type + ".json", 'w') as f:
					f.write(str(event_list))
			print("data successfully collected")
		except Exception as e:
			print("Problem Occured: ", e)

	def collect_issues_comments(self, args):
		repo_list = self.get_repo(args)
		print(repo_list)
		try:
			for repo_name in repo_list:
				repo = self.organization.get_repo(repo_name)
				issue_comment_list = []
				num_of_issue_comments = 0
				for comment in repo.get_issues_comments():
					comment_dict = {}
					comment_dict['id'] = comment.id
					comment_dict['user'] = comment.user
					comment_dict['body'] = comment.body
					comment_dict['issue_url'] = comment.issue_url
					issue_comment_list.append(comment_dict)

					num_of_issue_comments += 1
					print(num_of_issue_comments)

				with open(args.org + "/" + repo_name + "/" + args.event_type + "/" + args.org + "-" + repo_name + "-" +
						  args.event_type + ".json", 'w') as f:
					f.write(str(issue_comment_list))

			print("data successfully collected")
		except Exception as e:
			print("Problem occured:", e)

	def collect_issues(self, args):
		"""collect the data of the issue event in a given repository may be all repository or one repository"""
		# call a get_repo function
		repo_list = self.get_repo(args)
		print(repo_list)
		try:
			for repo_name in repo_list:
				repo = self.organization.get_repo(repo_name)

				issue_list = []
				num_of_issue = 0
				print("total number of " + args.state + " issue is: ", repo.get_issues(state=args.state).totalCount)
				for issue in repo.get_issues(state=args.state):
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

					num_of_issue += 1
					print(args.state + "issue: ", num_of_issue)

				# finalissue = "\n".join(str(row) for row in issue_list)
				with open(args.org + "/" + repo_name + "/" + args.event_type + "/" + args.org + "-" + repo_name + "-" +
						  args.state + "-" + args.event_type + ".json", 'w') as f:
					f.write(str(issue_list))

				self.sleeper()

			print("data successfully collected")
		except Exception as e:
			print("Problem Occured: ", e)

	def sleeper(self):
        # add sleeping time after requesting each page
		sleep_time = self.sleep_time_length + self.sleep_time_range * random.random()
		print("\n\tSleeping for", sleep_time, "seconds.")
		time.sleep(sleep_time)

	def main(self):

		# get the arguments from the terminal
		args = self.get_arguments()

		# validate the given arguments
		self.validate_arguments(args)

		# then create a github instance
		self.create_github_instance(args)

		# then call a create directory function
		self.create_directory(args)

		# identify the event type needed by the user and then go forward
		self.identify_event(args)

# Initialize the class
collect = Collect()
collect.main()
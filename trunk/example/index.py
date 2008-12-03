#!/usr/bin/python
#
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.appengine.api import datastore
from google.appengine.api import datastore_errors
from google.appengine.api import datastore_types
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from ranker import ranker

def GetRanker():
  key = datastore_types.Key.from_path("app", "default")
  try:
    return ranker.Ranker(datastore.Get(key)["ranker"])
  except datastore_errors.EntityNotFoundError:
    r = ranker.Ranker.Create([0, 10000], 100)
    app = datastore.Entity("app", name="default")
    app["ranker"] = r.rootkey
    datastore.Put(app)
    return r


class MainPage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, {}))


class SetScoreHandler(webapp.RequestHandler):
  def post(self):
    r = GetRanker()
    r.SetScore(self.request.get("name"), [int(self.request.get("score"))])
    self.redirect("/")


class QueryRankPage(webapp.RequestHandler):
  def get(self):
    r = GetRanker()
    rank = int(self.request.get("rank"))
    (score, rank_at_tie) = r.FindScore(rank)

    template_values = {"score": score, "rank": rank}
    if rank_at_tie < rank:
      template_values["tied"] = True
      template_values["rank_at_tie"] = rank_at_tie

    path = os.path.join(os.path.dirname(__file__), 'rank.html')
    self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/setscore', SetScoreHandler),
                                      ('/getrank', QueryRankPage)
                                      ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()

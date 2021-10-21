class Category:
  def __init__(self, name):
  self.name = name
  self.nlp_name = ""
  self.presenters = {}
  self.nominees = {}
  self.winner = ""


picture_drama = Category("Best Motion Picture - Drama")
picture_musical_or_comedy = Category("Best Motion Picture - Musical or Comedy")
picture_director = Category("Best Director - Motion Picture")
picture_actor_drama = Category("Best Performance by an Actor in a Motion Picture - Drama")
picture_actor_comedy = Category("Best Performance by an Actor in a Motion Picture - Comedy Or Musical")
picture_actress_drama = Category("Best Performance by an Actress in a Motion Picture - Drama")
picture_actress_comedy = Category("Best Performance by an Actress in a Motion Picture - Comedy Or Musical")
picture_actor_supporting = Category("Best Performance by an Actor In A Supporting Role in a Motion Picture")
picture_actress_supporting = Category("Best Performance by an Actress In A Supporting Role in a Motion Picture")
picture_screen_play= Category("Best Screenplay - Motion Picture")
picture_score = Category("Best Original Score - Motion Picture")
picture_song = Category("Best Original Song - Motion Picture")
picture_foreign = Category("Best Foreign Language Film")
picture_animated = Category("Best Animated Feature Film")
picture_cecil = Category("Cecil B. DeMille Award for Lifetime Achievement in Motion Pictures")
tv_drama = Category("Best Television Series - Drama")
tv_comedy = Category("Best Television Series - Comedy Or Musical")
tv_actor_drama = Category("Best Performance by an Actor In A Television Series - Drama")
tv_actor_comedy = Category("Best Performance by an Actor In A Television Series - Comedy Or Musical")
tv_actress_drama = Category("Best Performance by an Actress In A Television Series - Drama")
tv_actress_comedy = Category("Best Performance by an Actress In A Television Series - Comedy Or Musical")
tv_miniseries = Category("Best Mini-Series or Motion Picture made for Television")
tv_miniseries_actor = Category("Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television")
tv_miniseries_actress = Category("Best Performance by an Actress In A Mini-series or Motion Picture Made for Television")
tv_miniseries_actor_supporting = Category("Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television")
tv_miniseries_actress_supporting = Category("Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television")



category_list = [picture_drama,picture_musical_or_comedy,picture_director,picture_actor_drama,picture_actor_comedy,picture_actor_supporting,picture_actress_supporting,
picture_screen_play,picture_score,picture_song,picture_foreign,picture_animated,picture_cecil,tv_drama,tv_comedy,tv_actor_drama,tv_actress_drama,
tv_actress_comedy,tv_miniseries,tv_miniseries_actor,tv_miniseries_actress,tv_miniseries_actor_supporting,tv_miniseries_actress_supporting]
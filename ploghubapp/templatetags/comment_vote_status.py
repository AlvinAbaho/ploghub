from django import template

register = template.Library()

@register.filter
def get_vote_value(user_votes, comment_id):
    for vote in user_votes:
        if vote.comment.id == comment_id:
            return vote.value
    return 0

@register.filter
def get_post_vote_value(user_votes, post_id):
    for vote in user_votes:
        if vote.post.id == post_id:
            return vote.value
    return 0

@register.filter
def get_points(val):
    if val == 1 or val == -1:
        return "point"
    else:
        return "points"

@register.filter
def get_comments(val):
    if val == 1:
        return "comment"
    else:
        return "comments"
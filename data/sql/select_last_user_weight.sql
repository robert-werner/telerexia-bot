select weight
from weights
where user_id = {user_id} and group_id = {group_id}
order by weight_time desc
limit 1
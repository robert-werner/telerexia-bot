select *
from weights
where user_id = {user_id} and group_id = {group_id}
order by unix_time desc
limit 1
select row_number () over (order by weight asc), user_id, weight
from weights
where group_id = {group_id}
order by weight asc
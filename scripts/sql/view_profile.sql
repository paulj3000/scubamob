DROP VIEW if exists view_profile;
CREATE VIEW view_profile as
select u.id, u.username, u.first_name, u.last_name, ul.city as location, up.image as profile_image,
count(uf.id) as followers_count, count(ub.id) as buddy_count, count(dr.id) as reviews_count
from user u
left outer join user_location ul on ul.user_id = u.id
left outer join user_profile_image up on up.user_id = u.id
left outer join user_buddy ub on ub.user_id = u.id
left outer join user_follower uf on ub.user_id = u.id
left outer join divesite_review dr on dr.user_id = u.id
where ul.is_active=1;

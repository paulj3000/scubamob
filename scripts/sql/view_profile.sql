DROP VIEW if exists view_profile;
CREATE VIEW view_profile as
select
    u.id,
    u.username,
    u.first_name,
    u.last_name,
    u.is_private,
    u.is_active,
    (
        select ul.city from user_location ul
        where ul.user_id = u.id and ul.is_active = 1
        order by ul.id
        limit 1
    ) as location,
    (
        select up.image from user_profile_image up
        where up.user_id = u.id
        limit 1
    ) as profile_image,
    (
        select count(*) from user_follower uf
        where uf.user_id = u.id and uf.is_following = 1
    ) as followers_count,
    (
        select count(*) from user_buddy ub
        where ub.user_id = u.id
    ) as buddy_count,
    (
        select count(*) from divesite_review dr
        where dr.user_id = u.id
    ) as reviews_count
from user u;

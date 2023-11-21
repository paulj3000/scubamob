import React from 'react';

const Tags = (prop) => {
    return (
        <>
        {prop.tags.map(tag => (
            <a href={`/search?search=${tag.name}&location=${prop.location}`} key={tag.id} className="link-light">{tag.name}</a>
        ))}
        </>
    );
};

export default Tags;

import Reactions from './Reactions';

function Star(item) {
	/* this is WEIRD */
    if (item.id <= item.rating) {
        return <i className="bi bi-star-fill rating-color"></i>;
    }
    return <i className="bi bi-star"></i>;
}


const Review = (review) => {
    const id = review.id;
    const reactions = review.reactions;
    review = review.item;
    const divesite = review.divesite;

    return(
        <>
            <div className="card">
                <div className="card-body">
                    <h6 className="card-title">
                        <a href={divesite.url}>{divesite.name}</a>
                    </h6>
                    <div className="ratings">
                        <Star {...{'rating': review.rating, 'id': 1}} />
                        <Star {...{'rating': review.rating, 'id': 2}} />
                        <Star {...{'rating': review.rating, 'id': 3}} />
                        <Star {...{'rating': review.rating, 'id': 4}} />
                        <Star {...{'rating': review.rating, 'id': 5}} />
                        {review.review_date}
                    </div>
                    <p className="card-text">{review.review}</p>
                    <ul>
                        <li>Visibility: {review.visibility}</li>
                        <li>Water Temperature: {review.temp_c}&deg;C</li>
                    </ul>
                </div>
                <>
                    {
                        (() => { 
                            if (reactions) {
                                return <Reactions id={id} reactions={reactions} type="0" />
                            }
                        })()
                    }
                </>
            </div>
        </>
    )
}

export default Review;

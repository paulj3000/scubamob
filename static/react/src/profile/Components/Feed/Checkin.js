import Reactions from './Reactions';

function Star(item) {
	/* this is WEIRD */
    if (item.id <= item.rating) {
        return <i className="bi bi-star-fill rating-color"></i>;
    }
    return <i className="bi bi-star"></i>;
}


const Checkin = (checkin) => {
    const id = checkin.id;
    const reactions = checkin.reactions;
    checkin = checkin.item;
    const divesite = checkin.divesite;

    return(
        <>
            <div className="card">
                <div className="card-body">
                    <h6 className="card-title">
                        <a href={divesite.url}>{divesite.name}</a>
                    </h6>
                    <div className="ratings">
                        <Star {...{'rating': checkin.rating, 'id': 1}} />
                        <Star {...{'rating': checkin.rating, 'id': 2}} />
                        <Star {...{'rating': checkin.rating, 'id': 3}} />
                        <Star {...{'rating': checkin.rating, 'id': 4}} />
                        <Star {...{'rating': checkin.rating, 'id': 5}} />
                        {checkin.checkin_date}
                    </div>
                    <p className="card-text">{checkin.review}</p>
                    <ul>
                        <li>Visibility: {checkin.visibility}</li>
                        <li>Water Temperature: {checkin.temp_c}&deg;C</li>
                    </ul>
                </div>
                <>
                    {
                        (() => { 
                            if (reactions) {
                                return <Reactions id={id} reactions={reactions} />
                            }
                        })()
                    }
                </>
            </div>
        </>
    )
}

export default Checkin;

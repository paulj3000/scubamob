import React from 'react';

class Gallery extends React.Component {
    constructor(props) {
        super(props);
        self.id = props.id;
        this.state = {
            id: props.id,
            error: null,
            isLoaded: false,
            buddies: [],
            photos: 1,
        };
    }

    handleUpdate = (state) => {
        this.setState({photos: state})
    }

    componentDidMount() {

        fetch(`/api/profile/${self.id}/albums`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                        this.setState({
                        isLoaded: true,
                        buddies: result.buddies
                    });
                },

                // Note: it's important to handle errors here
                // instead of a catch() block so that we don't swallow
                // exceptions from actual bugs in components.
                (error) => {
                    this.setState({
                        isLoaded: true,
                        error
                    });
                }
            )
    }

    render() {
        const { error, isLoaded, buddies } = this.state;

        const active = 'nav-link active',
              inactive = 'nav-link';

        var photosActive = null;
        var photoAlbumsActive = null;
        switch(this.state.photos) {
            case 1:
                photoAlbumsActive = inactive;
                photosActive = active;
                break;
            case 2:
                photoAlbumsActive = active;
                photosActive = inactive;
                break;
        };

        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <>
                    <h1>Dive Gallery</h1>

                    <ul className="nav nav-pills">
                        <li className="nav-item">
                            <a className={photosActive} aria-current="page" href="#" onClick = {() => this.handleUpdate(1)}>Photos</a>
                        </li>
                        <li className="nav-item">
                            <a className={photoAlbumsActive} aria-current="pageAlbums" href="#" onClick = {() => this.handleUpdate(2)}>Photo Albums</a>
                        </li>
                    </ul>


                </>
            );
        }
    }
}

export default Gallery;

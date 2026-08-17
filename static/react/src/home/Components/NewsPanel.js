import React from 'react';


function NewsPanel(props) {
    const news = props.news || [];

    return (
        <div className="card mb-4">
            <div className="card-header">Dive News</div>
            <div className="card-body">
                {
                    news.length
                        ? news.map(article => (
                            <div className="mb-3" key={article.id}>
                                <a href={article.url}><strong>{article.title}</strong></a>
                                <p className="text-muted mb-0">{article.excerpt}</p>
                            </div>
                        ))
                        : <p className="text-muted mb-0">No news yet.</p>
                }
            </div>
        </div>
    );
}

export default NewsPanel;

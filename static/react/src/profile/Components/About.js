import React from "react";
import PropTypes from "prop-types";

export default class About extends React.Component {
  static propTypes = {
    value: PropTypes.string,
  };

  render() {
    return (
      <>
        <h2>The About Page</h2>
      </>
    );
  }
}

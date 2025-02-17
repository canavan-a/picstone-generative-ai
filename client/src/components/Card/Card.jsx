// PROP VALIDATION
import PropTypes from "prop-types";

// REACT IMPORTS
import { Link } from "react-router-dom";

// CONSTANTS
import styles from "./Card.module.scss";

// ENUMS
const MAX_CHARACTERS = 110;

const Card = ({ img, heading, description, link }) => {
  return (
    <div className={styles.card}>
      <img src={img} alt="" className={styles.img} />
      <h3 className={styles.heading}>{heading}</h3>
      <p className={styles.description}>
        {description.length > MAX_CHARACTERS
          ? `${description.substring(0, MAX_CHARACTERS)}...`
          : description}
      </p>
      <Link to={`${link}`} className={styles.link}>
        Read more
      </Link>
    </div>
  );
};

Card.propTypes = {
  img: PropTypes.string.isRequired,
  heading: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  link: PropTypes.string.isRequired,
};

export default Card;

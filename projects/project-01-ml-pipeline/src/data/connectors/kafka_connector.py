"""Kafka connector for streaming data ingestion."""

import json
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

from src.data.connectors.base import BaseConnector
from src.utils.logger import get_logger

logger = get_logger(__name__)


class KafkaConnector(BaseConnector):
    """Connector for reading data from Kafka topics."""

    def __init__(
        self,
        name: str = "kafka",
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
        group_id: Optional[str] = None,
        auto_offset_reset: str = "earliest",
        enable_auto_commit: bool = True,
        consumer_timeout_ms: int = 10000,
        max_poll_records: int = 500,
        security_protocol: str = "PLAINTEXT",
        sasl_mechanism: Optional[str] = None,
        sasl_plain_username: Optional[str] = None,
        sasl_plain_password: Optional[str] = None,
        value_deserializer: Optional[Callable] = None,
        key_deserializer: Optional[Callable] = None,
        **kwargs: Any,
    ):
        """Initialize Kafka connector.

        Args:
            name: Connector name
            bootstrap_servers: Kafka bootstrap servers (comma-separated)
            topic: Kafka topic to consume from
            group_id: Consumer group ID
            auto_offset_reset: What to do when no initial offset ('earliest', 'latest')
            enable_auto_commit: Whether to auto-commit offsets
            consumer_timeout_ms: Consumer timeout in milliseconds
            max_poll_records: Maximum records per poll
            security_protocol: Security protocol (PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)
            sasl_mechanism: SASL mechanism (PLAIN, SCRAM-SHA-256, etc.)
            sasl_plain_username: SASL username
            sasl_plain_password: SASL password
            value_deserializer: Function to deserialize message values
            key_deserializer: Function to deserialize message keys
            **kwargs: Additional KafkaConsumer arguments
        """
        config = {
            "bootstrap_servers": bootstrap_servers,
            "topic": topic,
            "group_id": group_id,
            "auto_offset_reset": auto_offset_reset,
            "enable_auto_commit": enable_auto_commit,
            "consumer_timeout_ms": consumer_timeout_ms,
            "max_poll_records": max_poll_records,
            "security_protocol": security_protocol,
            "sasl_mechanism": sasl_mechanism,
            "sasl_plain_username": sasl_plain_username,
            **kwargs,
        }
        super().__init__(name=name, config=config)

        self.bootstrap_servers = bootstrap_servers.split(",") if bootstrap_servers else []
        self.topic = topic
        self.group_id = group_id
        self.consumer_timeout_ms = consumer_timeout_ms
        self.max_poll_records = max_poll_records

        # Default deserializers (JSON)
        self.value_deserializer = value_deserializer or (
            lambda v: json.loads(v.decode("utf-8")) if v else None
        )
        self.key_deserializer = key_deserializer or (
            lambda k: k.decode("utf-8") if k else None
        )

        # Consumer and producer (lazy initialization)
        self._consumer: Optional[KafkaConsumer] = None
        self._producer: Optional[KafkaProducer] = None

    def connect(self) -> None:
        """Establish connection to Kafka.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Create consumer
            consumer_config = {
                "bootstrap_servers": self.bootstrap_servers,
                "group_id": self.group_id,
                "auto_offset_reset": self.config["auto_offset_reset"],
                "enable_auto_commit": self.config["enable_auto_commit"],
                "consumer_timeout_ms": self.consumer_timeout_ms,
                "max_poll_records": self.max_poll_records,
                "value_deserializer": self.value_deserializer,
                "key_deserializer": self.key_deserializer,
                "security_protocol": self.config["security_protocol"],
            }

            # Add SASL config if needed
            if self.config.get("sasl_mechanism"):
                consumer_config["sasl_mechanism"] = self.config["sasl_mechanism"]
                consumer_config["sasl_plain_username"] = self.config["sasl_plain_username"]
                consumer_config["sasl_plain_password"] = self.config["sasl_plain_password"]

            self._consumer = KafkaConsumer(**consumer_config)

            # Subscribe to topic
            if self.topic:
                self._consumer.subscribe([self.topic])

            logger.debug(f"Connected to Kafka: {self.name}")

        except KafkaError as e:
            raise ConnectionError(f"Failed to connect to Kafka: {e}")

    def disconnect(self) -> None:
        """Close connection to Kafka."""
        if self._consumer:
            self._consumer.close()
            self._consumer = None

        if self._producer:
            self._producer.close()
            self._producer = None

        logger.debug(f"Disconnected from Kafka: {self.name}")

    def read(
        self,
        query: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        max_records: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Read messages from Kafka topic.

        Args:
            query: Topic name (overrides configured topic)
            params: Additional parameters (not used for Kafka)
            max_records: Maximum number of records to read
            timeout_ms: Timeout in milliseconds
            **kwargs: Additional arguments

        Returns:
            DataFrame containing Kafka messages

        Raises:
            ConnectionError: If consumer not initialized
        """
        if not self._consumer:
            raise ConnectionError("Kafka consumer not initialized")

        # Subscribe to topic if different from configured
        topic = query or self.topic
        if topic and topic != self.topic:
            self._consumer.subscribe([topic])
            self.topic = topic

        # Set timeout
        timeout = timeout_ms or self.consumer_timeout_ms

        messages = []
        start_time = datetime.now()

        try:
            logger.info(f"Reading messages from Kafka topic: {self.topic}")

            # Poll messages
            for message in self._consumer:
                msg_data = {
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "timestamp": datetime.fromtimestamp(message.timestamp / 1000),
                    "key": message.key,
                    "value": message.value,
                }
                messages.append(msg_data)

                # Check limits
                if max_records and len(messages) >= max_records:
                    logger.debug(f"Reached max_records limit: {max_records}")
                    break

                # Check timeout
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                if elapsed >= timeout:
                    logger.debug(f"Reached timeout: {timeout}ms")
                    break

            # Convert to DataFrame
            if messages:
                df = pd.DataFrame(messages)

                # Flatten nested value dict if it exists
                if df["value"].apply(lambda x: isinstance(x, dict)).all():
                    value_df = pd.json_normalize(df["value"])
                    df = pd.concat(
                        [df.drop("value", axis=1), value_df.add_prefix("value.")], axis=1
                    )

                logger.info(f"Read {len(df)} messages from Kafka topic: {self.topic}")
                return df
            else:
                logger.warning(f"No messages received from Kafka topic: {self.topic}")
                return pd.DataFrame()

        except KafkaError as e:
            logger.error(f"Failed to read from Kafka: {e}")
            raise

    def consume_batch(
        self,
        batch_size: int = 100,
        timeout_ms: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Consume a batch of messages.

        Args:
            batch_size: Number of messages to consume
            timeout_ms: Timeout for batch in milliseconds

        Returns:
            List of message dictionaries
        """
        if not self._consumer:
            raise ConnectionError("Kafka consumer not initialized")

        messages = []

        try:
            # Poll with timeout
            msg_batch = self._consumer.poll(timeout_ms=timeout_ms, max_records=batch_size)

            for topic_partition, records in msg_batch.items():
                for message in records:
                    msg_data = {
                        "topic": message.topic,
                        "partition": message.partition,
                        "offset": message.offset,
                        "timestamp": datetime.fromtimestamp(message.timestamp / 1000),
                        "key": message.key,
                        "value": message.value,
                    }
                    messages.append(msg_data)

            logger.debug(f"Consumed batch of {len(messages)} messages")
            return messages

        except KafkaError as e:
            logger.error(f"Failed to consume batch: {e}")
            raise

    def stream(
        self,
        callback: Callable[[Dict[str, Any]], None],
        max_messages: Optional[int] = None,
    ) -> None:
        """Stream messages and apply callback function.

        Args:
            callback: Function to call for each message
            max_messages: Maximum number of messages to process (None for unlimited)
        """
        if not self._consumer:
            raise ConnectionError("Kafka consumer not initialized")

        message_count = 0

        try:
            logger.info(f"Starting message stream from topic: {self.topic}")

            for message in self._consumer:
                msg_data = {
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "timestamp": datetime.fromtimestamp(message.timestamp / 1000),
                    "key": message.key,
                    "value": message.value,
                }

                # Apply callback
                try:
                    callback(msg_data)
                except Exception as e:
                    logger.error(f"Error in callback for message offset {message.offset}: {e}")

                message_count += 1

                # Check limit
                if max_messages and message_count >= max_messages:
                    logger.info(f"Reached max_messages limit: {max_messages}")
                    break

            logger.info(f"Processed {message_count} messages from stream")

        except KafkaError as e:
            logger.error(f"Error in message stream: {e}")
            raise

    def produce(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        topic: Optional[str] = None,
        key: Optional[str] = None,
    ) -> None:
        """Produce messages to Kafka topic.

        Args:
            data: Message or list of messages to send
            topic: Topic to send to (uses configured topic if not provided)
            key: Message key
        """
        # Initialize producer if needed
        if not self._producer:
            producer_config = {
                "bootstrap_servers": self.bootstrap_servers,
                "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
                "key_serializer": lambda k: k.encode("utf-8") if k else None,
                "security_protocol": self.config["security_protocol"],
            }

            # Add SASL config if needed
            if self.config.get("sasl_mechanism"):
                producer_config["sasl_mechanism"] = self.config["sasl_mechanism"]
                producer_config["sasl_plain_username"] = self.config["sasl_plain_username"]
                producer_config["sasl_plain_password"] = self.config["sasl_plain_password"]

            self._producer = KafkaProducer(**producer_config)

        target_topic = topic or self.topic
        if not target_topic:
            raise ValueError("Topic must be provided")

        # Ensure data is a list
        messages = data if isinstance(data, list) else [data]

        try:
            for msg in messages:
                future = self._producer.send(target_topic, value=msg, key=key)
                # Wait for send to complete
                future.get(timeout=10)

            self._producer.flush()
            logger.info(f"Produced {len(messages)} messages to topic: {target_topic}")

        except KafkaError as e:
            logger.error(f"Failed to produce messages: {e}")
            raise

    def commit_offsets(self) -> None:
        """Manually commit current offsets."""
        if not self._consumer:
            raise ConnectionError("Kafka consumer not initialized")

        try:
            self._consumer.commit()
            logger.debug("Committed Kafka offsets")
        except KafkaError as e:
            logger.error(f"Failed to commit offsets: {e}")
            raise

    def seek_to_beginning(self) -> None:
        """Seek to the beginning of all assigned partitions."""
        if not self._consumer:
            raise ConnectionError("Kafka consumer not initialized")

        try:
            self._consumer.seek_to_beginning()
            logger.debug("Seeked to beginning of partitions")
        except KafkaError as e:
            logger.error(f"Failed to seek to beginning: {e}")
            raise

    def seek_to_end(self) -> None:
        """Seek to the end of all assigned partitions."""
        if not self._consumer:
            raise ConnectionError("Kafka consumer not initialized")

        try:
            self._consumer.seek_to_end()
            logger.debug("Seeked to end of partitions")
        except KafkaError as e:
            logger.error(f"Failed to seek to end: {e}")
            raise

    def get_kafka_info(self) -> Dict[str, Any]:
        """Get Kafka connection information.

        Returns:
            Dictionary containing Kafka metadata
        """
        info = {
            "bootstrap_servers": self.bootstrap_servers,
            "topic": self.topic,
            "group_id": self.group_id,
            "auto_offset_reset": self.config["auto_offset_reset"],
        }

        if self._consumer:
            info["assigned_partitions"] = [
                {"topic": tp.topic, "partition": tp.partition}
                for tp in self._consumer.assignment()
            ]

        return info

"""
Google Vertex AI Agent Builder MCP tool.

This tool provides integration with Google Vertex AI's Agent Builder for creating
and managing conversational AI agents with custom knowledge bases and tools.

Environment variables:
    GOOGLE_CLOUD_PROJECT: Google Cloud project ID (required)
    GOOGLE_APPLICATION_CREDENTIALS: Path to service account key file (required)
    VERTEX_AI_LOCATION: Vertex AI location/region (default: us-central1)
"""

import os
from typing import Any, Dict, List, Optional
import json

# Conditional imports for Google Cloud dependencies
try:
    from google.cloud import aiplatform
    from google.cloud import dialogflowcx_v3beta1 as dialogflowcx
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

from ..core.base import BaseMCPTool


class VertexAIAgentBuilderMCPTool(BaseMCPTool):
    """Google Vertex AI Agent Builder tool for conversational AI agents."""

    def __init__(self):
        """Initialize the Vertex AI Agent Builder tool."""
        super().__init__()
        
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError(
                "Google Cloud dependencies not available. Install with: "
                "pip install google-cloud-aiplatform google-cloud-dialogflowcx"
            )
        
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
        
        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)
        
        # Initialize Dialogflow CX client for Agent Builder
        self.dialogflow_client = dialogflowcx.AgentsClient()

    def create_agent(
        self,
        display_name: str,
        default_language_code: str = "en",
        time_zone: str = "America/New_York",
        description: Optional[str] = None,
        avatar_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversational AI agent.

        Args:
            display_name: Human-readable name for the agent
            default_language_code: Primary language for the agent
            time_zone: Time zone for the agent
            description: Optional description of the agent
            avatar_uri: Optional URI for agent avatar

        Returns:
            Dictionary containing agent creation results
        """
        try:
            # Create agent object
            agent = dialogflowcx.Agent(
                display_name=display_name,
                default_language_code=default_language_code,
                time_zone=time_zone,
                description=description,
                avatar_uri=avatar_uri,
                enable_stackdriver_logging=True,
                enable_spell_check=True,
                speech_to_text_settings=dialogflowcx.Agent.SpeechToTextSettings(
                    enable_speech_adaptation=True
                )
            )

            # Create the agent
            parent = f"projects/{self.project_id}/locations/{self.location}"
            request = dialogflowcx.CreateAgentRequest(
                parent=parent,
                agent=agent
            )

            operation = self.dialogflow_client.create_agent(request=request)
            agent_response = operation.result()

            return {
                "agent_id": agent_response.name.split("/")[-1],
                "agent_name": agent_response.display_name,
                "status": "created",
                "error": None
            }

        except Exception as e:
            return {
                "agent_id": None,
                "agent_name": display_name,
                "status": "failed",
                "error": str(e)
            }

    def create_intent(
        self,
        agent_id: str,
        display_name: str,
        training_phrases: List[str],
        parameters: Optional[List[Dict[str, Any]]] = None,
        responses: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an intent for the agent.

        Args:
            agent_id: ID of the agent
            display_name: Name for the intent
            training_phrases: List of example phrases that trigger this intent
            parameters: Optional list of parameters the intent can extract
            responses: Optional list of response messages

        Returns:
            Dictionary containing intent creation results
        """
        try:
            # Initialize intents client
            intents_client = dialogflowcx.IntentsClient()

            # Create training phrases
            training_phrase_parts = []
            for phrase in training_phrases:
                training_phrase_parts.append(
                    dialogflowcx.Intent.TrainingPhrase(
                        parts=[dialogflowcx.Intent.TrainingPhrase.Part(text=phrase)]
                    )
                )

            # Create parameters
            intent_parameters = []
            if parameters:
                for param in parameters:
                    intent_parameters.append(
                        dialogflowcx.Intent.Parameter(
                            id=param.get("id", ""),
                            entity_type=param.get("entity_type", ""),
                            is_list=param.get("is_list", False),
                            redact=param.get("redact", False)
                        )
                    )

            # Create responses
            intent_responses = []
            if responses:
                for response_text in responses:
                    intent_responses.append(
                        dialogflowcx.Intent.Message(
                            text=dialogflowcx.Intent.Message.Text(
                                text=[response_text]
                            )
                        )
                    )

            # Create intent
            intent = dialogflowcx.Intent(
                display_name=display_name,
                training_phrases=training_phrase_parts,
                parameters=intent_parameters,
                messages=intent_responses
            )

            # Create the intent
            parent = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            request = dialogflowcx.CreateIntentRequest(
                parent=parent,
                intent=intent
            )

            intent_response = intents_client.create_intent(request=request)

            return {
                "intent_id": intent_response.name.split("/")[-1],
                "intent_name": intent_response.display_name,
                "status": "created",
                "error": None
            }

        except Exception as e:
            return {
                "intent_id": None,
                "intent_name": display_name,
                "status": "failed",
                "error": str(e)
            }

    def create_flow(
        self,
        agent_id: str,
        display_name: str,
        description: Optional[str] = None,
        nlu_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a conversation flow for the agent.

        Args:
            agent_id: ID of the agent
            display_name: Name for the flow
            description: Optional description of the flow
            nlu_settings: Optional NLU settings

        Returns:
            Dictionary containing flow creation results
        """
        try:
            # Initialize flows client
            flows_client = dialogflowcx.FlowsClient()

            # Create NLU settings
            nlu_setting = dialogflowcx.Flow.NluSettings(
                model_type=dialogflowcx.Flow.NluSettings.ModelType.MODEL_TYPE_STANDARD,
                classification_threshold=0.3
            )
            if nlu_settings:
                nlu_setting = dialogflowcx.Flow.NluSettings(**nlu_settings)

            # Create flow
            flow = dialogflowcx.Flow(
                display_name=display_name,
                description=description,
                nlu_settings=nlu_setting
            )

            # Create the flow
            parent = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            request = dialogflowcx.CreateFlowRequest(
                parent=parent,
                flow=flow
            )

            flow_response = flows_client.create_flow(request=request)

            return {
                "flow_id": flow_response.name.split("/")[-1],
                "flow_name": flow_response.display_name,
                "status": "created",
                "error": None
            }

        except Exception as e:
            return {
                "flow_id": None,
                "flow_name": display_name,
                "status": "failed",
                "error": str(e)
            }

    def create_page(
        self,
        agent_id: str,
        flow_id: str,
        display_name: str,
        entry_fulfillment: Optional[Dict[str, Any]] = None,
        form: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a page within a flow.

        Args:
            agent_id: ID of the agent
            flow_id: ID of the flow
            display_name: Name for the page
            entry_fulfillment: Optional fulfillment to execute on page entry
            form: Optional form definition for the page

        Returns:
            Dictionary containing page creation results
        """
        try:
            # Initialize pages client
            pages_client = dialogflowcx.PagesClient()

            # Create fulfillment
            fulfillment = None
            if entry_fulfillment:
                fulfillment = dialogflowcx.Fulfillment(
                    messages=[
                        dialogflowcx.ResponseMessage(
                            text=dialogflowcx.ResponseMessage.Text(
                                text=[entry_fulfillment.get("message", "")]
                            )
                        )
                    ]
                )

            # Create form
            form_obj = None
            if form:
                parameters = []
                for param in form.get("parameters", []):
                    parameters.append(
                        dialogflowcx.Form.Parameter(
                            display_name=param.get("display_name", ""),
                            entity_type=param.get("entity_type", ""),
                            default_value=param.get("default_value", ""),
                            required=param.get("required", False)
                        )
                    )
                form_obj = dialogflowcx.Form(parameters=parameters)

            # Create page
            page = dialogflowcx.Page(
                display_name=display_name,
                entry_fulfillment=fulfillment,
                form=form_obj
            )

            # Create the page
            parent = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}/flows/{flow_id}"
            request = dialogflowcx.CreatePageRequest(
                parent=parent,
                page=page
            )

            page_response = pages_client.create_page(request=request)

            return {
                "page_id": page_response.name.split("/")[-1],
                "page_name": page_response.display_name,
                "status": "created",
                "error": None
            }

        except Exception as e:
            return {
                "page_id": None,
                "page_name": display_name,
                "status": "failed",
                "error": str(e)
            }

    def train_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Train the agent with current configuration.

        Args:
            agent_id: ID of the agent to train

        Returns:
            Dictionary containing training results
        """
        try:
            # Initialize agents client
            agents_client = dialogflowcx.AgentsClient()

            # Create training request
            name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            request = dialogflowcx.TrainAgentRequest(name=name)

            # Start training
            operation = agents_client.train_agent(request=request)
            operation.result()  # Wait for training to complete

            return {
                "agent_id": agent_id,
                "status": "trained",
                "error": None
            }

        except Exception as e:
            return {
                "agent_id": agent_id,
                "status": "failed",
                "error": str(e)
            }

    def detect_intent(
        self,
        agent_id: str,
        session_id: str,
        text: str,
        language_code: str = "en"
    ) -> Dict[str, Any]:
        """
        Detect intent from user input.

        Args:
            agent_id: ID of the agent
            session_id: Unique session identifier
            text: User input text
            language_code: Language code for the input

        Returns:
            Dictionary containing intent detection results
        """
        try:
            # Initialize sessions client
            sessions_client = dialogflowcx.SessionsClient()

            # Create session path
            session = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}/sessions/{session_id}"

            # Create text input
            text_input = dialogflowcx.TextInput(
                text=text,
                language_code=language_code
            )

            # Create query input
            query_input = dialogflowcx.QueryInput(text=text_input)

            # Create detect intent request
            request = dialogflowcx.DetectIntentRequest(
                session=session,
                query_input=query_input
            )

            # Detect intent
            response = sessions_client.detect_intent(request=request)

            # Extract results
            intent = response.query_result.intent
            fulfillment = response.query_result.fulfillment_text

            return {
                "intent_name": intent.display_name if intent else None,
                "confidence": response.query_result.intent_detection_confidence,
                "fulfillment_text": fulfillment,
                "parameters": dict(response.query_result.parameters),
                "error": None
            }

        except Exception as e:
            return {
                "intent_name": None,
                "confidence": 0.0,
                "fulfillment_text": "",
                "parameters": {},
                "error": str(e)
            }

    def list_agents(self) -> Dict[str, Any]:
        """
        List all agents in the project.

        Returns:
            Dictionary containing list of agents
        """
        try:
            # Initialize agents client
            agents_client = dialogflowcx.AgentsClient()

            # List agents
            parent = f"projects/{self.project_id}/locations/{self.location}"
            request = dialogflowcx.ListAgentsRequest(parent=parent)

            response = agents_client.list_agents(request=request)

            agents = []
            for agent in response:
                agents.append({
                    "id": agent.name.split("/")[-1],
                    "name": agent.display_name,
                    "default_language": agent.default_language_code,
                    "time_zone": agent.time_zone,
                    "description": agent.description
                })

            return {
                "agents": agents,
                "error": None
            }

        except Exception as e:
            return {
                "agents": [],
                "error": str(e)
            }

    def export_agent(
        self,
        agent_id: str,
        destination_uri: str,
        data_format: str = "BLOB"
    ) -> Dict[str, Any]:
        """
        Export agent configuration to a file.

        Args:
            agent_id: ID of the agent to export
            destination_uri: URI where the exported agent should be saved
            data_format: Format of the export (BLOB or JSON)

        Returns:
            Dictionary containing export results
        """
        try:
            # Initialize agents client
            agents_client = dialogflowcx.AgentsClient()

            # Create export request
            name = f"projects/{self.project_id}/locations/{self.location}/agents/{agent_id}"
            request = dialogflowcx.ExportAgentRequest(
                name=name,
                agent_uri=destination_uri,
                data_format=dialogflowcx.ExportAgentRequest.DataFormat.BLOB if data_format == "BLOB" else dialogflowcx.ExportAgentRequest.DataFormat.JSON
            )

            # Start export
            operation = agents_client.export_agent(request=request)
            result = operation.result()

            return {
                "agent_id": agent_id,
                "export_uri": destination_uri,
                "status": "exported",
                "error": None
            }

        except Exception as e:
            return {
                "agent_id": agent_id,
                "export_uri": destination_uri,
                "status": "failed",
                "error": str(e)
            }

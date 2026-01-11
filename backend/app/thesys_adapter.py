from typing import Dict, Any, List

class ThesysMockAdapter:
    """
    Simulates the C1 API by converting structured data into a Crayon UI Schema.
    Since we don't have the real C1 output from an LLM, we manually construct
    the standard Crayon component structure here.
    """

    @staticmethod
    def _create_card(title: str, subtitle: str, content: str, image_url: str = None, footer: str = None) -> Dict[str, Any]:
        """
        Helper to create a standard Card component in Crayon schema.
        """
        # Note: This is a hypothetical schema structure for Crayon since official docs are limit
        # We will assume a structure like: { type: "Card", props: { ... } }
        # The frontend will map this to the actual <Card> component.
        
        card_structure = {
            "type": "Card",
            "props": {
                "className": "w-full max-w-md bg-gray-800 text-white border-gray-700",
            },
            "children": [
                 {
                    "type": "CardHeader",
                    "children": [
                        {"type": "CardTitle", "props": {"className": "text-xl text-yellow-400"}, "children": [title]},
                        {"type": "CardDescription", "props": {"className": "text-gray-400"}, "children": [subtitle]}
                    ]
                 },
                 {
                    "type": "CardContent",
                    "children": [
                        {"type": "p", "props": {"className": "text-sm mt-2"}, "children": [content]}
                    ]
                 }
            ]
        }
        
        if image_url:
            # Insert image at top of content
            image_component = {
                "type": "img",
                "props": {
                    "src": image_url,
                    "alt": title,
                    "className": "w-full h-48 object-cover rounded-md mb-4"
                }
            }
            card_structure["children"][1]["children"].insert(0, image_component)

        if footer:
             card_structure["children"].append({
                "type": "CardFooter",
                "children": [{"type": "p", "props": {"className": "text-xs text-gray-500"}, "children": [footer]}]
             })

        return card_structure

    @staticmethod
    def _create_transaction_receipt(transaction_id: str, amount: str, recipient: str) -> Dict[str, Any]:
         return {
            "type": "Card",
            "props": {"className": "bg-green-900/20 border-green-500/50"},
            "children": [
                {
                    "type": "CardHeader", 
                    "children": [{"type": "CardTitle", "props": {"className": "text-green-400"}, "children": ["Transaction Successful"]}]
                },
                {
                    "type": "CardContent",
                    "children": [
                        {"type": "div", "props": {"className": "space-y-2"}, "children": [
                            {"type": "p", "children": [f"ID: {transaction_id}"]},
                            {"type": "p", "children": [f"Amount: {amount}"]},
                             {"type": "p", "children": [f"Sent to: {recipient}"]}
                        ]}
                    ]
                }
            ]
        }

    @staticmethod
    def _create_mindmap(center_node: str, related_nodes: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Creates a visual Node Graph (Mindmap) component.
        """
        # We simulate a graph using a central Card and surrounding "satellite" cards
        # In a real Thesys UI this would be a specific <GraphView> component
        
        satellites = []
        for node in related_nodes:
            satellites.append({
                "type": "div",
                "props": {"className": "flex flex-col items-center p-2 bg-gray-800 border border-purple-500 rounded-lg min-w-[100px]"},
                "children": [
                    {"type": "p", "props": {"className": "text-xs text-purple-300 mb-1"}, "children": [node['relation']]},
                    {"type": "p", "props": {"className": "text-sm font-bold text-white"}, "children": [node['label']]}
                ]
            })

        return {
            "type": "div",
            "props": {"className": "flex flex-col items-center space-y-4 w-full p-4 bg-gray-900/50 rounded-xl border border-gray-700"},
            "children": [
                # Title
                {"type": "h3", "props": {"className": "text-lg text-gray-400 uppercase tracking-widest"}, "children": ["Knowledge Graph"]},
                
                # Graph Container
                {
                    "type": "div", 
                    "props": {"className": "flex flex-wrap justify-center gap-6 items-center"},
                    "children": [
                         # Center Node
                        {
                            "type": "div",
                            "props": {"className": "p-6 bg-purple-900/40 border-2 border-purple-400 rounded-full shadow-[0_0_15px_rgba(168,85,247,0.5)] z-10"},
                            "children": [{"type": "h4", "props": {"className": "text-xl font-bold text-white"}, "children": [center_node]}]
                        },
                        
                        # Satellites
                        *satellites
                    ]
                }
            ]
        }

    def adapt_response(self, agent_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point. Takes raw agent data and returns a UI Schema.
        """
        ui_schema = []
        
        if agent_type == "ingestion":
            # Movie Card
            title = data.get("title", "Unknown Movie")
            subtitle = data.get("url", "Result from Wikipedia")
            content = data.get("summary", "No summary available.")
            
            # Try to find an image
            image = None
            if "images" in data and data["images"]:
                image = data["images"][0] # Naive first image
            # Or check fanart data if available in future
            
            ui_schema.append(self._create_card(title, subtitle, content, image_url=image))
        
        elif agent_type == "mindmap":
            # Knowledge Graph / Mindmap
            center = data.get("center", "Unknown")
            relations = data.get("relations", [])
            ui_schema.append(self._create_mindmap(center, relations))
            
        elif agent_type == "commerce":
            # Receipt
            ui_schema.append(self._create_transaction_receipt(
                data.get("transaction_id", "???"),
                data.get("amount", "$0.00"),
                data.get("recipient", "user")
            ))

        elif agent_type == "reasoning":
            # LLM Response Card
            response_text = data.get("response_text", "")
            # If the response is long, we might want to put it in a card
            if len(response_text) > 50:
                 ui_schema.append(self._create_card(
                    title="Movie Fan AI",
                    subtitle="Thinking Process",
                    content=response_text,
                    footer="Generated by Fireworks AI (Llama 3)"
                ))
            else:
                 # Just a bubble message (simulated by a small card for now)
                 ui_schema.append(self._create_card(
                    title="AI",
                    subtitle="",
                    content=response_text
                ))
            
        else:
            # Default text fallback
            ui_schema.append({
                "type": "p", 
                "props": {"children": "Processed by " + agent_type}
            })
            
        return {"ui_schema": ui_schema}

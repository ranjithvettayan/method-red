from typing import Dict, Any, Optional
from .base import BaseProvider
from .core.anthropic import AnthropicProvider
from .core.azure import AzureProvider
from .core.cohere import CohereProvider
from .core.deepseek import DeepSeekProvider
from .core.fireworks_ai import FireworksAIProvider
from .core.google import GoogleProvider
from .core.groq import GroqProvider
from .core.mistral import MistralProvider
from .core.openai import OpenAIProvider
from .core.togetherai import TogetherAIProvider
from .cloud.amazon_bedrock import AmazonBedrockProvider
from .cloud.azure_cognitive_services import AzureCognitiveServicesProvider
from .cloud.cloudflare_workers_ai import CloudflareWorkersAIProvider
from .cloud.google_vertex import GoogleVertexProvider
from .cloud.google_vertex_anthropic import GoogleVertexAnthropicProvider
from .cloud.ovhcloud import OvhcloudProvider
from .cloud.scaleway import ScalewayProvider
from .cloud.vercel import VercelProvider
from .cloud.vultr import VultrProvider
from .chinese.alibaba import AlibabaProvider
from .chinese.alibaba_cn import AlibabaCNProvider
from .chinese.kimi_for_coding import KimiForCodingProvider
from .chinese.minimax import MinimaxProvider
from .chinese.minimax_cn import MinimaxCNProvider
from .chinese.modelscope import ModelscopeProvider
from .chinese.moonshotai import MoonshotaiProvider
from .chinese.moonshotai_cn import MoonshotaiCNProvider
from .chinese.zhipuai import ZhipuaiProvider
from .chinese.zhipuai_coding_plan import ZhipuaiCodingPlanProvider
from .specialized.github_copilot import GithubCopilotProvider
from .specialized.github_models import GithubModelsProvider
from .specialized.huggingface import HuggingfaceProvider
from .specialized.llama import LlamaProvider
from .specialized.lmstudio import LmstudioProvider
from .specialized.ollama_cloud import OllamaCloudProvider
from .specialized.wandb import WandbProvider
from .specialized.xai import XAIProvider
from .research.cerebras import CerebrasProvider
from .research.nebius import NebiusProvider
from .research.nvidia import NvidiaProvider
from .routing.agentrouter import AgentrouterProvider
from .routing.fastrouter import FastrouterProvider
from .routing.openrouter import OpenrouterProvider
from .routing.perplexity import PerplexityProvider
from .other.aihubmix import AihubmixProvider
from .other.bailing import BailingProvider
from .other.baseten import BasetenProvider
from .other.chutes import ChutesProvider
from .other.cortecs import CortecsProvider
from .other.deepinfra import DeepinfraProvider
from .other.iflowcn import IflowcnProvider
from .other.inception import InceptionProvider
from .other.inference import InferenceProvider
from .other.io_net import IoNetProvider
from .other.lucidquery import LucidqueryProvider
from .other.morph import MorphProvider
from .other.opencode import OpencodeProvider
from .other.poe import POEProvider
from .other.requesty import RequestyProvider
from .other.siliconflow import SiliconflowProvider
from .other.submodel import SubmodelProvider
from .other.synthetic import SyntheticProvider
from .other.upstage import UpstageProvider
from .other.v0 import V0Provider
from .other.venice import VeniceProvider
from .other.zai import ZAIProvider
from .other.zai_coding_plan import ZaiCodingPlanProvider
from .other.zenmux import ZenmuxProvider


class ProviderRegistry:
    """Registry for all LLM providers"""

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self._register_providers()

    def _register_providers(self):
        """Register all available providers"""
        self.providers['anthropic'] = AnthropicProvider()
        self.providers['azure'] = AzureProvider()
        self.providers['cohere'] = CohereProvider()
        self.providers['deepseek'] = DeepSeekProvider()
        self.providers['fireworks-ai'] = FireworksAIProvider()
        self.providers['google'] = GoogleProvider()
        self.providers['groq'] = GroqProvider()
        self.providers['mistral'] = MistralProvider()
        self.providers['openai'] = OpenAIProvider()
        self.providers['togetherai'] = TogetherAIProvider()
        self.providers['amazon-bedrock'] = AmazonBedrockProvider()
        self.providers['azure-cognitive-services'] = AzureCognitiveServicesProvider()
        self.providers['cloudflare-workers-ai'] = CloudflareWorkersAIProvider()
        self.providers['google-vertex'] = GoogleVertexProvider()
        self.providers['google-vertex-anthropic'] = GoogleVertexAnthropicProvider()
        self.providers['ovhcloud'] = OvhcloudProvider()
        self.providers['scaleway'] = ScalewayProvider()
        self.providers['vercel'] = VercelProvider()
        self.providers['vultr'] = VultrProvider()
        self.providers['alibaba'] = AlibabaProvider()
        self.providers['alibaba-cn'] = AlibabaCNProvider()
        self.providers['kimi-for-coding'] = KimiForCodingProvider()
        self.providers['minimax'] = MinimaxProvider()
        self.providers['minimax-cn'] = MinimaxCNProvider()
        self.providers['modelscope'] = ModelscopeProvider()
        self.providers['moonshotai'] = MoonshotaiProvider()
        self.providers['moonshotai-cn'] = MoonshotaiCNProvider()
        self.providers['zhipuai'] = ZhipuaiProvider()
        self.providers['zhipuai-coding-plan'] = ZhipuaiCodingPlanProvider()
        self.providers['github-copilot'] = GithubCopilotProvider()
        self.providers['github-models'] = GithubModelsProvider()
        self.providers['huggingface'] = HuggingfaceProvider()
        self.providers['llama'] = LlamaProvider()
        self.providers['lmstudio'] = LmstudioProvider()
        self.providers['ollama-cloud'] = OllamaCloudProvider()
        self.providers['wandb'] = WandbProvider()
        self.providers['xai'] = XAIProvider()
        self.providers['cerebras'] = CerebrasProvider()
        self.providers['nebius'] = NebiusProvider()
        self.providers['nvidia'] = NvidiaProvider()
        self.providers['agentrouter'] = AgentrouterProvider()
        self.providers['fastrouter'] = FastrouterProvider()
        self.providers['openrouter'] = OpenrouterProvider()
        self.providers['perplexity'] = PerplexityProvider()
        self.providers['aihubmix'] = AihubmixProvider()
        self.providers['bailing'] = BailingProvider()
        self.providers['baseten'] = BasetenProvider()
        self.providers['chutes'] = ChutesProvider()
        self.providers['cortecs'] = CortecsProvider()
        self.providers['deepinfra'] = DeepinfraProvider()
        self.providers['iflowcn'] = IflowcnProvider()
        self.providers['inception'] = InceptionProvider()
        self.providers['inference'] = InferenceProvider()
        self.providers['io-net'] = IoNetProvider()
        self.providers['lucidquery'] = LucidqueryProvider()
        self.providers['morph'] = MorphProvider()
        self.providers['opencode'] = OpencodeProvider()
        self.providers['poe'] = POEProvider()
        self.providers['requesty'] = RequestyProvider()
        self.providers['siliconflow'] = SiliconflowProvider()
        self.providers['submodel'] = SubmodelProvider()
        self.providers['synthetic'] = SyntheticProvider()
        self.providers['upstage'] = UpstageProvider()
        self.providers['v0'] = V0Provider()
        self.providers['venice'] = VeniceProvider()
        self.providers['zai'] = ZAIProvider()
        self.providers['zai-coding-plan'] = ZaiCodingPlanProvider()
        self.providers['zenmux'] = ZenmuxProvider()

    def get_provider(self, provider_id: str) -> Optional[BaseProvider]:
        """Get provider instance by ID (checks custom providers first)"""
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return custom_registry.get_provider(provider_id)
        
        return self.providers.get(provider_id)

    def get_api_key(self, provider_id: str, model_id: str = None) -> Optional[str]:
        """Get API key for a provider"""
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return custom_registry.get_api_key(provider_id, model_id)
        
        provider = self.providers.get(provider_id)
        if provider:
            return provider.get_api_key(model_id)
        return None

    def get_model_string(self, provider_id: str, model_id: str) -> str:
        """Get model string for CrewAI"""
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return custom_registry.get_model_string(provider_id, model_id)
        
        provider = self.providers.get(provider_id)
        if provider:
            return provider.get_model_string(model_id)
        return f"{provider_id}/{model_id}"

    def get_base_url(self, provider_id: str) -> Optional[str]:
        """Get base URL for OpenAI-compatible providers.
        
        Returns None for providers natively supported by LiteLLM.
        Returns the API base URL for OpenAI-compatible providers.
        """
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return custom_registry.get_base_url(provider_id)
        
        provider = self.providers.get(provider_id)
        if provider:
            return provider.get_base_url()
        return None

    def is_provider_configured(self, provider_id: str) -> bool:
        """Check if a provider is properly configured"""
        # Check custom providers first
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        if custom_registry.has_provider(provider_id):
            return True  # Custom providers are always "configured" if they exist
        
        provider = self.providers.get(provider_id)
        return provider is not None and provider.is_configured()

    def get_configured_providers(self) -> Dict[str, BaseProvider]:
        """Get all configured providers (including custom)"""
        result = {pid: provider for pid, provider in self.providers.items() if provider.is_configured()}
        
        # Add custom providers
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        for provider in custom_registry.get_all_providers():
            result[provider.provider_id] = provider
        
        return result

    def get_available_providers(self) -> Dict[str, BaseProvider]:
        """Get all available providers (whether configured or not)"""
        result = self.providers.copy()
        
        # Add custom providers
        from .custom import get_custom_registry
        custom_registry = get_custom_registry()
        for provider in custom_registry.get_all_providers():
            result[provider.provider_id] = provider
        
        return result
    
    def reload_custom_providers(self):
        """Reload custom providers from database"""
        from .custom import reload_custom_providers
        reload_custom_providers()


# Global provider registry
provider_registry = ProviderRegistry()

"""
Token tracking utility for LLM usage monitoring and pricing calculations.

Tracks input/output tokens for each LLM call and provides comprehensive
usage statistics for cost analysis.
"""

import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class TokenUsage:
    """Individual token usage record for a single LLM call."""
    timestamp: datetime
    tool_name: str
    method_name: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_estimate: float = 0.0
    call_duration: float = 0.0


@dataclass
class TokenSummary:
    """Summary of token usage across all tools."""
    total_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_cost_estimate: float = 0.0
    tool_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    model_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class TokenTracker:
    """
    Thread-safe token tracking system for monitoring LLM usage.
    
    Tracks all LLM calls across the application and provides detailed
    usage statistics for pricing calculations.
    """
    
    def __init__(self):
        """Initialize the token tracker."""
        self._lock = threading.Lock()
        self._usage_records: List[TokenUsage] = []
        self._tool_stats: Dict[str, Dict[str, Any]] = {}
        self._model_stats: Dict[str, Dict[str, Any]] = {}
        
        # Token pricing (per 1M tokens) - update as needed
        self._pricing = {
            "gemini-2.5-flash": {"input": 0.075, "output": 0.30},  # $0.075/$0.30 per 1M tokens
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        }
    
    def track_call(
        self,
        tool_name: str,
        method_name: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        call_duration: float = 0.0
    ) -> None:
        """
        Track a single LLM call with token usage.
        
        Args:
            tool_name: Name of the tool making the call
            method_name: Name of the method being called
            model: LLM model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            call_duration: Duration of the call in seconds
        """
        with self._lock:
            total_tokens = input_tokens + output_tokens
            
            # Calculate cost estimate
            cost_estimate = 0.0
            if model in self._pricing:
                pricing = self._pricing[model]
                input_cost = (input_tokens / 1_000_000) * pricing["input"]
                output_cost = (output_tokens / 1_000_000) * pricing["output"]
                cost_estimate = input_cost + output_cost
            
            # Create usage record
            usage = TokenUsage(
                timestamp=datetime.now(),
                tool_name=tool_name,
                method_name=method_name,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_estimate=cost_estimate,
                call_duration=call_duration
            )
            
            self._usage_records.append(usage)
            
            # Update tool statistics
            if tool_name not in self._tool_stats:
                self._tool_stats[tool_name] = {
                    "total_calls": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "methods": {}
                }
            
            tool_stats = self._tool_stats[tool_name]
            tool_stats["total_calls"] += 1
            tool_stats["total_input_tokens"] += input_tokens
            tool_stats["total_output_tokens"] += output_tokens
            tool_stats["total_tokens"] += total_tokens
            tool_stats["total_cost"] += cost_estimate
            
            # Update method statistics
            if method_name not in tool_stats["methods"]:
                tool_stats["methods"][method_name] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0
                }
            
            method_stats = tool_stats["methods"][method_name]
            method_stats["calls"] += 1
            method_stats["input_tokens"] += input_tokens
            method_stats["output_tokens"] += output_tokens
            method_stats["total_tokens"] += total_tokens
            method_stats["cost"] += cost_estimate
            
            # Update model statistics
            if model not in self._model_stats:
                self._model_stats[model] = {
                    "total_calls": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0
                }
            
            model_stats = self._model_stats[model]
            model_stats["total_calls"] += 1
            model_stats["total_input_tokens"] += input_tokens
            model_stats["total_output_tokens"] += output_tokens
            model_stats["total_tokens"] += total_tokens
            model_stats["total_cost"] += cost_estimate
    
    def get_summary(self) -> TokenSummary:
        """
        Get comprehensive token usage summary.
        
        Returns:
            TokenSummary with detailed usage statistics
        """
        with self._lock:
            total_calls = len(self._usage_records)
            total_input_tokens = sum(record.input_tokens for record in self._usage_records)
            total_output_tokens = sum(record.output_tokens for record in self._usage_records)
            total_tokens = total_input_tokens + total_output_tokens
            total_cost = sum(record.cost_estimate for record in self._usage_records)
            
            return TokenSummary(
                total_calls=total_calls,
                total_input_tokens=total_input_tokens,
                total_output_tokens=total_output_tokens,
                total_tokens=total_tokens,
                total_cost_estimate=total_cost,
                tool_breakdown=self._tool_stats.copy(),
                model_breakdown=self._model_stats.copy()
            )
    
    def get_tool_usage(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get usage statistics for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with tool usage statistics or None if not found
        """
        with self._lock:
            return self._tool_stats.get(tool_name)
    
    def get_model_usage(self, model: str) -> Optional[Dict[str, Any]]:
        """
        Get usage statistics for a specific model.
        
        Args:
            model: Name of the model
            
        Returns:
            Dictionary with model usage statistics or None if not found
        """
        with self._lock:
            return self._model_stats.get(model)
    
    def clear(self) -> None:
        """Clear all tracking data."""
        with self._lock:
            self._usage_records.clear()
            self._tool_stats.clear()
            self._model_stats.clear()
    
    def print_summary(self) -> None:
        """Print a formatted summary of token usage."""
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("LLM TOKEN USAGE SUMMARY")
        print("="*80)
        print(f"Total LLM Calls: {summary.total_calls}")
        print(f"Total Input Tokens: {summary.total_input_tokens:,}")
        print(f"Total Output Tokens: {summary.total_output_tokens:,}")
        print(f"Total Tokens: {summary.total_tokens:,}")
        print(f"Estimated Cost: ${summary.total_cost_estimate:.4f}")
        print()
        
        if summary.tool_breakdown:
            print("TOOL BREAKDOWN:")
            print("-" * 40)
            for tool_name, stats in summary.tool_breakdown.items():
                print(f"{tool_name}:")
                print(f"  Calls: {stats['total_calls']}")
                print(f"  Input Tokens: {stats['total_input_tokens']:,}")
                print(f"  Output Tokens: {stats['total_output_tokens']:,}")
                print(f"  Total Tokens: {stats['total_tokens']:,}")
                print(f"  Cost: ${stats['total_cost']:.4f}")
                if stats['methods']:
                    print("  Methods:")
                    for method, method_stats in stats['methods'].items():
                        print(f"    {method}: {method_stats['calls']} calls, {method_stats['total_tokens']:,} tokens, ${method_stats['cost']:.4f}")
                print()
        
        if summary.model_breakdown:
            print("MODEL BREAKDOWN:")
            print("-" * 40)
            for model, stats in summary.model_breakdown.items():
                print(f"{model}:")
                print(f"  Calls: {stats['total_calls']}")
                print(f"  Input Tokens: {stats['total_input_tokens']:,}")
                print(f"  Output Tokens: {stats['total_output_tokens']:,}")
                print(f"  Total Tokens: {stats['total_tokens']:,}")
                print(f"  Cost: ${stats['total_cost']:.4f}")
                print()
        
        print("="*80)


# Global token tracker instance
token_tracker = TokenTracker()

#!/usr/bin/env python3
"""
Comprehensive Serena LSP Error Analysis Tool

Real LSP integration using Serena and SolidLSP libraries for comprehensive error analysis.
Produces the exact output format: ERRORS: N [⚠️ Critical: X] [👉 Major: Y] [🔍 Minor: Z]

Usage:
    python serena_analyzer.py <repo_path> [--verbose]
    python serena_analyzer.py . --verbose
"""

import argparse
import ast
import json
import logging
import os
import sys
import time
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Serena and SolidLSP imports for real LSP integration
try:
    from solidlsp.ls_types import (
        DiagnosticSeverity, Diagnostic, Position, Range, MarkupContent, Location, 
        MarkupKind, CompletionItemKind, CompletionItem, UnifiedSymbolInformation, 
        SymbolKind, SymbolTag
    )
    from solidlsp.ls_utils import TextUtils, PathUtils, FileUtils, PlatformId, SymbolUtils
    from solidlsp.ls_request import LanguageServerRequest
    from solidlsp.ls_logger import LanguageServerLogger, LogLine
    from solidlsp.ls_handler import SolidLanguageServerHandler, Request, LanguageServerTerminatedException
    from solidlsp.ls import SolidLanguageServer, LSPFileBuffer
    from solidlsp.lsp_protocol_handler.lsp_constants import LSPConstants
    from solidlsp.lsp_protocol_handler.lsp_requests import LspRequest
    from solidlsp.lsp_protocol_handler.lsp_types import (
        DocumentDiagnosticReportKind, ErrorCodes, LSPErrorCodes, DiagnosticSeverity as LSPDiagnosticSeverity,
        DiagnosticTag, InitializeError, WorkspaceDiagnosticParams, WorkspaceDiagnosticReport,
        WorkspaceDiagnosticReportPartialResult, PublishDiagnosticsParams, RelatedFullDocumentDiagnosticReport,
        RelatedUnchangedDocumentDiagnosticReport, UnchangedDocumentDiagnosticReport, FullDocumentDiagnosticReport,
        DiagnosticOptions, WorkspaceFullDocumentDiagnosticReport, WorkspaceUnchangedDocumentDiagnosticReport,
        DiagnosticRelatedInformation, DiagnosticWorkspaceClientCapabilities, DiagnosticClientCapabilities,
        PublishDiagnosticsClientCapabilities
    )
    from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo, LSPError, MessageType
    from serena.symbol import (
        LanguageServerSymbolRetriever, ReferenceInLanguageServerSymbol, LanguageServerSymbol,
        Symbol, PositionInFile, LanguageServerSymbolLocation
    )
    from serena.text_utils import MatchedConsecutiveLines, TextLine, LineType
    from serena.project import Project
    from serena.gui_log_viewer import GuiLogViewer, LogLevel, GuiLogViewerHandler
    from serena.code_editor import CodeEditor
    from serena.cli import (
        PromptCommands, ToolCommands, ProjectCommands, SerenaConfigCommands, ContextCommands,
        ModeCommands, TopLevelCommands, AutoRegisteringGroup, ProjectType
    )
    
    SERENA_AVAILABLE = True
    
except ImportError as e:
    print(f"⚠️  Warning: Serena/SolidLSP libraries not available: {e}")
    print("📋 Falling back to basic AST analysis mode")
    print("💡 To use full LSP capabilities, install Serena and SolidLSP libraries")
    SERENA_AVAILABLE = False


@dataclass
class FunctionInfo:
    """Information about a function where an error occurs."""
    name: str
    line_start: int
    line_end: int
    function_type: str = "function"  # 'function', 'method', 'class'
    parent_class: Optional[str] = None
    is_public: bool = True
    complexity_score: int = 1
    symbol_info: Optional[Any] = None  # Serena LanguageServerSymbol when available


@dataclass 
class EnhancedDiagnostic:
    """Enhanced diagnostic with function attribution and severity classification."""
    file_path: str
    line: int
    column: int
    severity: str  # CRITICAL, MAJOR, MINOR, INFO
    message: str
    code: Optional[str] = None
    source: str = "analyzer"
    function_name: str = "unknown"
    function_info: Optional[FunctionInfo] = None
    lsp_diagnostic: Optional[Any] = None  # Original LSP Diagnostic when available


class EnhancedSeverity:
    """Advanced severity classification with visual indicators."""
    
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR" 
    MINOR = "MINOR"
    INFO = "INFO"
    
    SEVERITY_ICONS = {
        CRITICAL: "⚠️",
        MAJOR: "👉", 
        MINOR: "🔍",
        INFO: "ℹ️"
    }
    
    @classmethod
    def classify_lsp_diagnostic(cls, lsp_diagnostic: Any, function_context: Optional[str] = None) -> str:
        """Classify LSP diagnostic severity with enhanced business logic."""
        if not SERENA_AVAILABLE:
            return cls._classify_basic_diagnostic(lsp_diagnostic, function_context)
        
        # Map LSP severity to enhanced severity
        if hasattr(lsp_diagnostic, 'severity'):
            lsp_severity = lsp_diagnostic.severity
            
            # Critical: LSP errors that indicate serious issues
            if lsp_severity == DiagnosticSeverity.Error:
                message = getattr(lsp_diagnostic, 'message', '').lower()
                
                # Security and critical runtime issues
                critical_keywords = [
                    "security", "vulnerability", "injection", "exploit", "unsafe",
                    "null pointer", "buffer overflow", "memory leak", "deadlock",
                    "syntax error", "import error", "module not found", "name error"
                ]
                
                if any(keyword in message for keyword in critical_keywords):
                    return cls.CRITICAL
                
                # Main function errors are more critical
                if function_context and any(func in function_context.lower() 
                                         for func in ["main", "__main__", "init", "setup"]):
                    return cls.CRITICAL
                
                return cls.MAJOR
            
            # Major: LSP warnings that indicate significant issues
            elif lsp_severity == DiagnosticSeverity.Warning:
                message = getattr(lsp_diagnostic, 'message', '').lower()
                
                major_keywords = [
                    "deprecated", "performance", "inefficient", "unused", "undefined",
                    "type error", "compatibility", "breaking change"
                ]
                
                if any(keyword in message for keyword in major_keywords):
                    return cls.MAJOR
                
                return cls.MINOR
            
            # Minor: LSP info and hints
            elif lsp_severity in [DiagnosticSeverity.Information, DiagnosticSeverity.Hint]:
                return cls.MINOR
        
        return cls.MINOR
    
    @classmethod
    def _classify_basic_diagnostic(cls, diagnostic_info: Any, function_context: Optional[str] = None) -> str:
        """Fallback classification for basic mode."""
        if isinstance(diagnostic_info, dict):
            message = diagnostic_info.get('message', '').lower()
        else:
            message = str(diagnostic_info).lower()
        
        # Critical indicators
        critical_keywords = [
            "security", "vulnerability", "injection", "exploit", "unsafe",
            "syntax error", "import error", "module not found", "name error"
        ]
        
        if any(keyword in message for keyword in critical_keywords):
            return cls.CRITICAL
        
        # Major indicators  
        major_keywords = [
            "deprecated", "performance", "inefficient", "unused", "undefined",
            "type error", "value error", "high complexity"
        ]
        
        if any(keyword in message for keyword in major_keywords):
            return cls.MAJOR
        
        return cls.MINOR


class SerenaLSPAnalyzer:
    """Real LSP analyzer using Serena and SolidLSP libraries."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.project: Optional[Project] = None
        self.language_server: Optional[SolidLanguageServer] = None
        self.symbol_retriever: Optional[LanguageServerSymbolRetriever] = None
        
    def setup_project(self, repo_path: str) -> bool:
        """Set up Serena project for LSP analysis."""
        if not SERENA_AVAILABLE:
            return False
            
        try:
            self.logger.info(f"🔧 Setting up Serena project for: {repo_path}")
            
            # Create Serena project
            self.project = Project.from_path(repo_path)
            
            if not self.project:
                self.logger.error("Failed to create Serena project")
                return False
            
            # Initialize language server
            self.language_server = SolidLanguageServer(
                project=self.project,
                logger=LanguageServerLogger() if self.verbose else None
            )
            
            # Start language server
            if not self.language_server.start():
                self.logger.error("Failed to start language server")
                return False
            
            # Initialize symbol retriever
            self.symbol_retriever = LanguageServerSymbolRetriever(
                language_server=self.language_server,
                project=self.project
            )
            
            self.logger.info("✅ Serena project setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Serena project: {e}")
            return False
    
    def get_lsp_diagnostics(self, file_path: str) -> List[Diagnostic]:
        """Get real LSP diagnostics for a file."""
        if not SERENA_AVAILABLE or not self.language_server:
            return []
        
        try:
            # Request diagnostics from LSP server
            diagnostics = self.language_server.get_diagnostics(file_path)
            return diagnostics or []
            
        except LSPError as e:
            if self.verbose:
                self.logger.debug(f"LSP error for {os.path.basename(file_path)}: {e}")
            return []
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"Error getting diagnostics for {os.path.basename(file_path)}: {e}")
            return []
    
    def get_symbol_at_position(self, file_path: str, line: int, column: int) -> Optional[LanguageServerSymbol]:
        """Get symbol information at a specific position."""
        if not SERENA_AVAILABLE or not self.symbol_retriever:
            return None
        
        try:
            position = PositionInFile(file_path=file_path, line=line, column=column)
            symbol = self.symbol_retriever.get_symbol_at_position(position)
            return symbol
            
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"Error getting symbol at {file_path}:{line}:{column}: {e}")
            return None
    
    def get_function_symbols(self, file_path: str) -> List[LanguageServerSymbol]:
        """Get all function symbols in a file."""
        if not SERENA_AVAILABLE or not self.symbol_retriever:
            return []
        
        try:
            symbols = self.symbol_retriever.get_symbols_in_file(file_path)
            function_symbols = [
                symbol for symbol in symbols 
                if symbol.kind in [SymbolKind.Function, SymbolKind.Method, SymbolKind.Constructor]
            ]
            return function_symbols
            
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"Error getting function symbols for {os.path.basename(file_path)}: {e}")
            return []
    
    def cleanup(self):
        """Clean up LSP resources."""
        if self.language_server:
            try:
                self.language_server.stop()
            except Exception as e:
                if self.verbose:
                    self.logger.debug(f"Error stopping language server: {e}")


class FallbackAnalyzer:
    """Fallback AST-based analyzer when Serena is not available."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.function_cache: Dict[str, List[FunctionInfo]] = {}
    
    def extract_functions_from_file(self, file_path: str) -> List[FunctionInfo]:
        """Extract function information using AST parsing."""
        cache_key = f"{file_path}:{os.path.getmtime(file_path)}"
        if cache_key in self.function_cache:
            return self.function_cache[cache_key]
        
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            class FunctionVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.current_class = None
                    self.functions = []
                
                def visit_ClassDef(self, node):
                    old_class = self.current_class
                    self.current_class = node.name
                    self.generic_visit(node)
                    self.current_class = old_class
                
                def visit_FunctionDef(self, node):
                    self._process_function(node)
                    self.generic_visit(node)
                
                def visit_AsyncFunctionDef(self, node):
                    self._process_function(node, is_async=True)
                    self.generic_visit(node)
                
                def _process_function(self, node, is_async=False):
                    function_type = "method" if self.current_class else "function"
                    if is_async:
                        function_type = f"async_{function_type}"
                    
                    func_info = FunctionInfo(
                        name=node.name,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        function_type=function_type,
                        parent_class=self.current_class,
                        is_public=not node.name.startswith('_'),
                        complexity_score=self._estimate_complexity(node)
                    )
                    
                    self.functions.append(func_info)
                
                def _estimate_complexity(self, node):
                    """Simple complexity estimation."""
                    complexity = 1
                    for child in ast.walk(node):
                        if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                            complexity += 1
                        elif isinstance(child, (ast.And, ast.Or)):
                            complexity += 1
                    return min(complexity, 10)
            
            visitor = FunctionVisitor()
            visitor.visit(tree)
            functions = visitor.functions
            
            self.function_cache[cache_key] = functions
            
        except SyntaxError as e:
            # Create error function info for syntax errors
            func_info = FunctionInfo(
                name="<syntax_error>",
                line_start=e.lineno or 1,
                line_end=e.lineno or 1,
                function_type="error"
            )
            functions = [func_info]
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"Failed to parse {os.path.basename(file_path)}: {e}")
        
        return functions
    
    def find_function_at_line(self, file_path: str, line_number: int) -> Optional[FunctionInfo]:
        """Find the function that contains the given line number."""
        functions = self.extract_functions_from_file(file_path)
        
        for func in functions:
            if func.line_start <= line_number <= func.line_end:
                return func
        
        return None
    
    def analyze_file_basic(self, file_path: str) -> List[EnhancedDiagnostic]:
        """Basic file analysis using AST and pattern matching."""
        diagnostics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for syntax errors
            try:
                ast.parse(content)
            except SyntaxError as e:
                func_info = self.find_function_at_line(file_path, e.lineno or 1)
                func_name = func_info.name if func_info else "unknown"
                
                diagnostic = EnhancedDiagnostic(
                    file_path=file_path,
                    line=e.lineno or 1,
                    column=e.offset or 1,
                    severity=EnhancedSeverity.CRITICAL,
                    message=f"Syntax error: {e.msg}",
                    code="syntax-error",
                    source="python-ast",
                    function_name=func_name,
                    function_info=func_info
                )
                diagnostics.append(diagnostic)
                return diagnostics
            
            # Analyze each line for common issues
            for line_num, line in enumerate(lines, 1):
                line_issues = self._analyze_line(file_path, line_num, line)
                diagnostics.extend(line_issues)
            
            # Analyze imports and functions
            import_issues = self._analyze_imports(file_path, content)
            diagnostics.extend(import_issues)
            
            function_issues = self._analyze_functions(file_path)
            diagnostics.extend(function_issues)
            
        except Exception as e:
            if self.verbose:
                self.logger.warning(f"Failed to analyze {os.path.basename(file_path)}: {e}")
        
        return diagnostics
    
    def _analyze_line(self, file_path: str, line_num: int, line: str) -> List[EnhancedDiagnostic]:
        """Analyze a single line for issues."""
        diagnostics = []
        
        # Find function context
        func_info = self.find_function_at_line(file_path, line_num)
        func_name = func_info.name if func_info else "unknown"
        
        # Check line length
        if len(line) > 88:
            severity = EnhancedSeverity._classify_basic_diagnostic("line too long", func_name)
            diagnostic = EnhancedDiagnostic(
                file_path=file_path,
                line=line_num,
                column=89,
                severity=severity,
                message=f"Line too long ({len(line)} > 88 characters)",
                code="line-too-long",
                source="style-checker",
                function_name=func_name,
                function_info=func_info
            )
            diagnostics.append(diagnostic)
        
        # Check for TODO comments
        if "TODO" in line or "FIXME" in line or "HACK" in line:
            severity = EnhancedSeverity._classify_basic_diagnostic("todo comment", func_name)
            diagnostic = EnhancedDiagnostic(
                file_path=file_path,
                line=line_num,
                column=line.find("TODO") + 1 if "TODO" in line else line.find("FIXME") + 1,
                severity=severity,
                message="TODO/FIXME comment found - consider addressing",
                code="todo-comment",
                source="maintenance-checker",
                function_name=func_name,
                function_info=func_info
            )
            diagnostics.append(diagnostic)
        
        # Check for print statements
        if re.search(r'\bprint\s*\(', line):
            severity = EnhancedSeverity._classify_basic_diagnostic("print statement", func_name)
            diagnostic = EnhancedDiagnostic(
                file_path=file_path,
                line=line_num,
                column=line.find("print") + 1,
                severity=severity,
                message="Consider using logging instead of print statements",
                code="print-statement",
                source="best-practice-checker",
                function_name=func_name,
                function_info=func_info
            )
            diagnostics.append(diagnostic)
        
        return diagnostics
    
    def _analyze_imports(self, file_path: str, content: str) -> List[EnhancedDiagnostic]:
        """Analyze import statements."""
        diagnostics = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Simple unused import check
                        if alias.name not in content.replace(f"import {alias.name}", ""):
                            severity = EnhancedSeverity._classify_basic_diagnostic("unused import")
                            diagnostic = EnhancedDiagnostic(
                                file_path=file_path,
                                line=node.lineno,
                                column=node.col_offset + 1,
                                severity=severity,
                                message=f"Unused import: {alias.name}",
                                code="unused-import",
                                source="import-checker",
                                function_name="<module>"
                            )
                            diagnostics.append(diagnostic)
        
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"Import analysis failed for {os.path.basename(file_path)}: {e}")
        
        return diagnostics
    
    def _analyze_functions(self, file_path: str) -> List[EnhancedDiagnostic]:
        """Analyze functions for various issues."""
        diagnostics = []
        functions = self.extract_functions_from_file(file_path)
        
        for func in functions:
            # Check for missing docstrings in public functions
            if func.is_public and func.function_type in ["function", "method"]:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    # Simple docstring check
                    has_docstring = False
                    for i in range(func.line_start, min(func.line_start + 3, len(lines))):
                        if '"""' in lines[i] or "'''" in lines[i]:
                            has_docstring = True
                            break
                    
                    if not has_docstring:
                        severity = EnhancedSeverity._classify_basic_diagnostic("missing docstring", func.name)
                        diagnostic = EnhancedDiagnostic(
                            file_path=file_path,
                            line=func.line_start,
                            column=1,
                            severity=severity,
                            message=f"Missing docstring for public {func.function_type}: {func.name}",
                            code="missing-docstring",
                            source="docstring-checker",
                            function_name=func.name,
                            function_info=func
                        )
                        diagnostics.append(diagnostic)
                
                except Exception:
                    pass
            
            # Check for high complexity
            if func.complexity_score > 7:
                severity = EnhancedSeverity._classify_basic_diagnostic("high complexity", func.name)
                diagnostic = EnhancedDiagnostic(
                    file_path=file_path,
                    line=func.line_start,
                    column=1,
                    severity=severity,
                    message=f"High complexity function (score: {func.complexity_score})",
                    code="high-complexity",
                    source="complexity-checker",
                    function_name=func.name,
                    function_info=func
                )
                diagnostics.append(diagnostic)
        
        return diagnostics


class ComprehensiveSerenaAnalyzer:
    """Main analyzer that coordinates LSP and fallback analysis."""
    
    def __init__(self, verbose: bool = False, max_workers: int = 4):
        self.verbose = verbose
        self.max_workers = max_workers
        self.lock = threading.Lock()
        
        # Set up logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize analyzers
        self.serena_analyzer = SerenaLSPAnalyzer(verbose) if SERENA_AVAILABLE else None
        self.fallback_analyzer = FallbackAnalyzer(verbose)
        
        # Statistics
        self.total_files = 0
        self.processed_files = 0
        self.failed_files = 0
        self.total_diagnostics = 0
        
        # Show mode
        if SERENA_AVAILABLE:
            self.logger.info("🚀 Using Serena LSP mode with real language server integration")
        else:
            self.logger.info("📋 Using fallback AST analysis mode")
    
    def find_source_files(self, repo_path: str) -> List[str]:
        """Find all source files in the repository."""
        source_files = []
        
        # File extensions to analyze
        extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp'}
        
        # Directories to ignore
        ignore_dirs = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
            'build', 'dist', 'target', '.pytest_cache', '.mypy_cache'
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    source_files.append(file_path)
        
        return source_files
    
    def analyze_file(self, file_path: str) -> List[EnhancedDiagnostic]:
        """Analyze a single file using the best available method."""
        diagnostics = []
        
        try:
            if SERENA_AVAILABLE and self.serena_analyzer and self.serena_analyzer.language_server:
                # Use real LSP analysis
                diagnostics = self._analyze_file_with_lsp(file_path)
            else:
                # Use fallback analysis
                if file_path.endswith('.py'):
                    diagnostics = self.fallback_analyzer.analyze_file_basic(file_path)
                else:
                    diagnostics = self._basic_file_analysis(file_path)
            
            with self.lock:
                self.processed_files += 1
                self.total_diagnostics += len(diagnostics)
            
            if self.verbose and diagnostics:
                self.logger.debug(f"Found {len(diagnostics)} issues in {os.path.basename(file_path)}")
        
        except Exception as e:
            with self.lock:
                self.failed_files += 1
            self.logger.warning(f"Failed to analyze {os.path.basename(file_path)}: {e}")
        
        return diagnostics
    
    def _analyze_file_with_lsp(self, file_path: str) -> List[EnhancedDiagnostic]:
        """Analyze file using real LSP integration."""
        diagnostics = []
        
        if not self.serena_analyzer:
            return diagnostics
        
        try:
            # Get LSP diagnostics
            lsp_diagnostics = self.serena_analyzer.get_lsp_diagnostics(file_path)
            
            # Get function symbols for context
            function_symbols = self.serena_analyzer.get_function_symbols(file_path)
            
            # Create function lookup
            function_lookup = {}
            for symbol in function_symbols:
                if hasattr(symbol, 'location') and hasattr(symbol.location, 'range'):
                    start_line = symbol.location.range.start.line + 1  # LSP is 0-based
                    end_line = symbol.location.range.end.line + 1
                    
                    func_info = FunctionInfo(
                        name=symbol.name,
                        line_start=start_line,
                        line_end=end_line,
                        function_type="method" if hasattr(symbol, 'container_name') else "function",
                        parent_class=getattr(symbol, 'container_name', None),
                        symbol_info=symbol
                    )
                    
                    for line in range(start_line, end_line + 1):
                        function_lookup[line] = func_info
            
            # Process LSP diagnostics
            for lsp_diag in lsp_diagnostics:
                line = lsp_diag.range.start.line + 1  # Convert to 1-based
                column = lsp_diag.range.start.character + 1
                
                # Find function context
                func_info = function_lookup.get(line)
                func_name = func_info.name if func_info else "unknown"
                
                # Classify severity
                severity = EnhancedSeverity.classify_lsp_diagnostic(lsp_diag, func_name)
                
                # Create enhanced diagnostic
                enhanced_diag = EnhancedDiagnostic(
                    file_path=file_path,
                    line=line,
                    column=column,
                    severity=severity,
                    message=lsp_diag.message,
                    code=str(lsp_diag.code) if lsp_diag.code else None,
                    source=lsp_diag.source or "lsp",
                    function_name=func_name,
                    function_info=func_info,
                    lsp_diagnostic=lsp_diag
                )
                
                diagnostics.append(enhanced_diag)
        
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"LSP analysis failed for {os.path.basename(file_path)}: {e}")
        
        return diagnostics
    
    def _basic_file_analysis(self, file_path: str) -> List[EnhancedDiagnostic]:
        """Basic analysis for non-Python files."""
        diagnostics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Check line length
                if len(line.rstrip()) > 120:
                    severity = EnhancedSeverity._classify_basic_diagnostic("line too long")
                    diagnostic = EnhancedDiagnostic(
                        file_path=file_path,
                        line=line_num,
                        column=121,
                        severity=severity,
                        message=f"Line too long ({len(line.rstrip())} > 120 characters)",
                        code="line-too-long",
                        source="basic-checker"
                    )
                    diagnostics.append(diagnostic)
                
                # Check for TODO comments
                if "TODO" in line or "FIXME" in line:
                    severity = EnhancedSeverity._classify_basic_diagnostic("todo comment")
                    diagnostic = EnhancedDiagnostic(
                        file_path=file_path,
                        line=line_num,
                        column=line.find("TODO") + 1 if "TODO" in line else line.find("FIXME") + 1,
                        severity=severity,
                        message="TODO/FIXME comment found",
                        code="todo-comment",
                        source="basic-checker"
                    )
                    diagnostics.append(diagnostic)
        
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"Basic analysis failed for {os.path.basename(file_path)}: {e}")
        
        return diagnostics
    
    def analyze_repository(self, repo_path: str) -> List[EnhancedDiagnostic]:
        """Analyze entire repository."""
        start_time = time.time()
        
        self.logger.info(f"🔍 Starting comprehensive Serena analysis of: {repo_path}")
        
        # Setup Serena project if available
        if SERENA_AVAILABLE and self.serena_analyzer:
            if not self.serena_analyzer.setup_project(repo_path):
                self.logger.warning("⚠️  Serena setup failed, falling back to AST analysis")
                self.serena_analyzer = None
        
        # Find all source files
        source_files = self.find_source_files(repo_path)
        self.total_files = len(source_files)
        
        if self.total_files == 0:
            self.logger.warning("No source files found")
            return []
        
        self.logger.info(f"📊 Found {self.total_files} source files to analyze")
        
        # Analyze files in parallel
        all_diagnostics = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze_file, file_path): file_path 
                for file_path in source_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    diagnostics = future.result()
                    all_diagnostics.extend(diagnostics)
                except Exception as e:
                    self.logger.error(f"Error processing {os.path.basename(file_path)}: {e}")
        
        analysis_time = time.time() - start_time
        
        self.logger.info("=" * 60)
        self.logger.info("📋 SERENA ANALYSIS COMPLETE")
        self.logger.info("=" * 60)
        self.logger.info(f"✅ Files processed: {self.processed_files}")
        self.logger.info(f"❌ Files failed: {self.failed_files}")
        self.logger.info(f"🔍 Total diagnostics: {self.total_diagnostics}")
        self.logger.info(f"⏱️  Analysis time: {analysis_time:.2f} seconds")
        self.logger.info("=" * 60)
        
        return all_diagnostics
    
    def format_output(self, diagnostics: List[EnhancedDiagnostic], project_name: str = "project") -> str:
        """Format diagnostics in the requested output format."""
        if not diagnostics:
            return "ERRORS: 0 [⚠️ Critical: 0] [👉 Major: 0] [🔍 Minor: 0]\nNo errors found."
        
        # Count by severity
        severity_counts = Counter(diag.severity for diag in diagnostics)
        total_count = len(diagnostics)
        
        critical_count = severity_counts.get(EnhancedSeverity.CRITICAL, 0)
        major_count = severity_counts.get(EnhancedSeverity.MAJOR, 0)
        minor_count = severity_counts.get(EnhancedSeverity.MINOR, 0)
        info_count = severity_counts.get(EnhancedSeverity.INFO, 0)
        
        # Create header
        header_parts = [
            f"ERRORS: {total_count}",
            f"[⚠️ Critical: {critical_count}]",
            f"[👉 Major: {major_count}]",
            f"[🔍 Minor: {minor_count}]"
        ]
        
        if info_count > 0:
            header_parts.append(f"[ℹ️ Info: {info_count}]")
        
        header = " ".join(header_parts)
        
        # Sort diagnostics by severity priority
        severity_priority = {
            EnhancedSeverity.CRITICAL: 0,
            EnhancedSeverity.MAJOR: 1,
            EnhancedSeverity.MINOR: 2,
            EnhancedSeverity.INFO: 3
        }
        
        sorted_diagnostics = sorted(diagnostics, key=lambda d: (
            severity_priority.get(d.severity, 4),
            d.file_path.lower(),
            d.line
        ))
        
        # Format each diagnostic entry
        output_lines = [header]
        
        for i, diag in enumerate(sorted_diagnostics, 1):
            # Get severity icon
            severity_icon = EnhancedSeverity.SEVERITY_ICONS.get(diag.severity, "❓")
            
            # Format file path
            try:
                display_path = os.path.relpath(diag.file_path)
                if not display_path.startswith(project_name):
                    display_path = f"{project_name}/{display_path}"
            except ValueError:
                display_path = diag.file_path
            
            # Format function information
            if diag.function_info and diag.function_info.parent_class:
                function_part = f"Class.Method - '{diag.function_info.parent_class}.{diag.function_name}'"
            elif diag.function_info and diag.function_info.function_type == "method":
                function_part = f"Method - '{diag.function_name}'"
            elif diag.function_name != "unknown":
                function_part = f"Function - '{diag.function_name}'"
            else:
                function_part = f"Line {diag.line}"
            
            # Format error message
            error_reason = diag.message
            if diag.code:
                error_reason = f"{diag.code}: {error_reason}"
            
            # Truncate long messages
            if len(error_reason) > 100:
                error_reason = error_reason[:97] + "..."
            
            # Create entry
            entry = f"{i} {severity_icon}- {display_path} / {function_part} [{error_reason}]"
            output_lines.append(entry)
        
        return '\n'.join(output_lines)
    
    def cleanup(self):
        """Clean up resources."""
        if self.serena_analyzer:
            self.serena_analyzer.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Serena LSP Error Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python serena_analyzer.py .
    python serena_analyzer.py /path/to/repo --verbose
    python serena_analyzer.py . --max-workers 8
        """
    )
    
    parser.add_argument(
        'repository',
        help='Repository path to analyze'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of parallel workers (default: 4)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.repository):
        print(f"❌ Error: Repository path does not exist: {args.repository}")
        sys.exit(1)
    
    print("🚀 COMPREHENSIVE SERENA LSP ERROR ANALYSIS")
    print("=" * 60)
    print(f"📁 Repository: {args.repository}")
    print(f"👥 Max workers: {args.max_workers}")
    print(f"📋 Verbose: {args.verbose}")
    if SERENA_AVAILABLE:
        print("🔧 Mode: Real LSP integration with Serena/SolidLSP")
    else:
        print("📋 Mode: Fallback AST analysis")
    print("=" * 60)
    
    try:
        analyzer = ComprehensiveSerenaAnalyzer(verbose=args.verbose, max_workers=args.max_workers)
        diagnostics = analyzer.analyze_repository(args.repository)
        
        # Format and display results
        project_name = os.path.basename(os.path.abspath(args.repository))
        result = analyzer.format_output(diagnostics, project_name)
        
        print("\n" + "=" * 60)
        print("📋 SERENA ANALYSIS RESULTS")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
        # Cleanup
        analyzer.cleanup()
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

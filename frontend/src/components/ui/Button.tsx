import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import { cn } from "@/utils/cn";

const buttonVariants = cva(
    "inline-flex items-center justify-center rounded-lg text-sm font-bold tracking-widest uppercase transition-all duration-200 focus-visible:outline-none disabled:opacity-50 disabled:pointer-events-none active:scale-95",
    {
        variants: {
            variant: {
                default: "bg-black border border-accent-orange text-accent-orange hover:bg-accent-orange hover:text-black glow-orange",
                destructive: "border border-red-500/50 text-red-500 hover:bg-red-500 hover:text-white",
                outline: "border border-white/10 bg-transparent hover:bg-white/5 text-slate-300 hover:text-white",
                secondary: "bg-black border border-accent-lime text-accent-lime hover:bg-accent-lime hover:text-black glow-lime",
                ghost: "hover:bg-white/5 text-slate-500 hover:text-slate-200",
                link: "underline-offset-4 hover:underline text-accent-orange",
                premium: "bg-black border border-accent-purple text-accent-purple hover:bg-accent-purple hover:text-black shadow-[0_0_20px_rgba(168,85,247,0.15)]",
            },
            size: {
                default: "h-11 px-6",
                sm: "h-9 px-4 text-xs",
                lg: "h-14 px-10 text-base",
                icon: "h-11 w-11",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    }
);

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    isLoading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, isLoading, children, ...props }, ref) => {
        return (
            <button
                className={cn(buttonVariants({ variant, size, className }))}
                ref={ref}
                disabled={isLoading || props.disabled}
                {...props}
            >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {children}
            </button>
        );
    }
);
Button.displayName = "Button";

export { Button, buttonVariants };

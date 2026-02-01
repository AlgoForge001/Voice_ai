import * as React from "react"
import { cn } from "@/utils/cn"

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    accent?: 'orange' | 'purple' | 'green';
}

const Card = React.forwardRef<
    HTMLDivElement,
    CardProps
>(({ className, accent, ...props }, ref) => (
    <div
        ref={ref}
        className={cn(
            "glass-card",
            accent === 'orange' && "accent-border-orange",
            accent === 'purple' && "accent-border-purple",
            accent === 'green' && "accent-border-green",
            className
        )}
        {...props}
    />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn("flex flex-col space-y-1.5 p-6 border-b border-white/5", className)}
        {...props}
    />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
    <h3
        ref={ref}
        className={cn(
            "text-base font-bold tracking-widest uppercase text-slate-300",
            className
        )}
        {...props}
    />
))
CardTitle.displayName = "CardTitle"

const CardContent = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6", className)} {...props} />
))
CardContent.displayName = "CardContent"

export { Card, CardHeader, CardTitle, CardContent }
